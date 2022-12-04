# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 12:28:51 2022
@author: Gerardo Ortíz Montufar
"""

from resources.NP_GUI import Ui_MainWindow, QtWidgets, QtCore
from resources.bucle_abierto import open_loop
from resources.controlStim import CntrlStim
from resources.trapecio_traslapado import getTrapecio_traslapado
from threading import Thread


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self._translate = QtCore.QCoreApplication.translate
        # Setup matplotlib canvas to hold four graphs in the given layout, with a toolbar
        self.ui.GrafCanvas.setupCanvas(toolbar = True)
        self.t1 = []
        self.t2 = []
        self.ch1 = []
        self.ch2 = []
        #activar eventos bucle abierto
        self.ui.cadency_box.valueChanged.connect(self.updateNumRepeticionesBA)
        self.ui.t_tot_stim_box_ba.valueChanged.connect(self.updateNumRepeticionesBA)
        self.ui.dutycycle_box.valueChanged.connect(self.updateTiempoCanalesBA)
        self.ui.buttonBA.clicked.connect(self.iniciarBA)

    def updateNumRepeticionesBA(self):
        repeticiones = int(round(self.ui.t_tot_stim_box_ba.value()*self.ui.cadency_box.value()/60))
        self.ui.numRepeticiones_ba.setText(f"{repeticiones}")
        self.updateTiempoCanalesBA()
    
    def updateTiempoCanalesBA(self):
        T_zancada = 60/self.ui.cadency_box.value()*1000
        tiempoCH1 = T_zancada*self.ui.dutycycle_box.value()/100
        tiempoCH2 = T_zancada*(100-self.ui.dutycycle_box.value())/100
        self.ui.t_totalxrepCH1.setText(f"{round(tiempoCH1,3)}")
        self.ui.t_totalxrepCH2.setText(f"{round(tiempoCH2,3)}")

    def iniciarBA(self):
        """
        tiempo, cadency, dutycycle, 
        max_current1,max_current2,
        msi, pw,
        t_ascent1, t_descent1,
        t_ascent2, t_descent2,
        channels = (6,7)
        """
        self.programa = open_loop(
            self.ui.t_tot_stim_box_ba.value(),
            self.ui.cadency_box.value(),
            self.ui.dutycycle_box.value()/100,
            self.ui.current_max_ch1_box_ba.value(),
            self.ui.current_max_ch2_box_ba.value(),
            self.ui.msi_box_ba.value(),
            self.ui.pw_box_ba.value(),
            self.ui.t_subidaCH1_box_ba.value(),
            self.ui.t_bajadaCH1_box_ba.value(),
            self.ui.t_subidaCH2_box_ba.value(),
            self.ui.t_bajadaCH2_box_ba.value(),
            (self.ui.ch1_box_ba.value()-1,self.ui.ch2_box_ba.value()-1)
        )
        self.ui.buttonBA.setText(self._translate("MainWindow", "Parar"))
        self.ui.buttonBA.disconnect()
        self.ui.buttonBA.clicked.connect(self.programa.stop)
        self.programa.rutina_wdg()
        self.programa.fin.connect(self.fin)
        self.programa.stimuli.connect(self.update_canales)
        self.programa.rutina_wdg()
        self.programa.start()
        self.ui.Status_txt.clear()
        self.ui.Status_txt.insertPlainText("Inicializado\n")

    def fin(self,msj):
        self.ui.Status_txt.insertPlainText(msj)
        self.update_canvas()
        self.t1,self.t2,self.ch1,self.ch2=[],[],[],[]
        self.ui.buttonBA.setText(self._translate("MainWindow", "Iniciar"))
        self.ui.buttonBA.disconnect()
        self.ui.buttonBA.clicked.connect(self.iniciarBA)

    def update_canales(self,tiempo,c,canal):
        t = tiempo - self.programa.t0
        if canal == self.ui.ch1_box_ba.value()-1:
            self.ch1.append(c)
            self.t1.append(t)
        else:
            self.ch2.append(c)
            self.t2.append(t)

    def update_canvas(self):
        ax = self.ui.GrafCanvas.axes[0]
        ax.clear()
        ax.stem(self.t1,self.ch1,label = "CH1",linefmt='green',markerfmt='go')
        ax.stem(self.t2,self.ch2,label = "CH2")
        ax.legend()
        ax.grid()
        self.ui.GrafCanvas.draw()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())