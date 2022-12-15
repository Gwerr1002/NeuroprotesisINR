# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 12:28:51 2022
@author: Gerardo Ortíz Montufar
"""

from resources.NP_GUI import Ui_MainWindow, QtWidgets, QtCore
from resources.bucle_abierto import open_loop, playsound, time
from resources.controlStim import CntrlStim
from resources.trapecio_traslapado import getTrapecio_traslapado
from resources.from_file import load
from threading import Thread, Event


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
        self.ch1_actual = int()
        #activar eventos bucle abierto
        self.ui.cadency_box.valueChanged.connect(self.updateNumRepeticionesBA)
        self.ui.t_tot_stim_box_ba.valueChanged.connect(self.updateNumRepeticionesBA)
        self.ui.dutycycle_box.valueChanged.connect(self.updateTiempoCanalesBA)
        self.ui.buttonBA.clicked.connect(self.iniciarBA)
        #activar eventos trapecio traslapado
        self.ui.buttonTT.clicked.connect(self.iniciarTT)
        #activar eventos de modo usuario (cargar de archivo)
        self.ui.button_load_file.clicked.connect(self.cargarDic)
        self.ui.button_fromfile.clicked.connect(self.iniciarUSRMODE)

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
        self.ch1_actual = int(self.ui.ch1_box_ba.value())
        self.programa = open_loop(
            self.ui.t_tot_stim_box_ba.value(),
            self.ui.cadency_box.value(),
            self.ui.dutycycle_box.value()/100,
            self.ui.current_max_ch1_box_ba.value(),
            self.ui.current_max_ch2_box_ba.value(),
            int(self.ui.msi_box_ba.value()),
            int(self.ui.pw_box_ba.value()),
            self.ui.t_subidaCH1_box_ba.value(),
            self.ui.t_bajadaCH1_box_ba.value(),
            self.ui.t_subidaCH2_box_ba.value(),
            self.ui.t_bajadaCH2_box_ba.value(),
            (int(self.ui.ch1_box_ba.value()-1),int(self.ui.ch2_box_ba.value()-1))
        )
        self.ui.buttonBA.setText(self._translate("MainWindow", "Parar"))
        self.ui.buttonBA.disconnect()
        self.ui.buttonBA.clicked.connect(self.programa.stop)
        self.programa.rutina_wdg()
        self.programa.fin.connect(self.finBA)
        self.programa.stimuli.connect(self.update_canales)
        self.programa.rutina_wdg()
        self.programa.start()
        self.ui.Status_txt.clear()
        self.ui.Status_txt.insertPlainText("Inicializado\n")

    def finBA(self,msj):
        self.ui.Status_txt.insertPlainText(msj)
        self.update_canvas()
        self.t1,self.t2,self.ch1,self.ch2=[],[],[],[]
        self.ui.buttonBA.setText(self._translate("MainWindow", "Iniciar"))
        self.ui.buttonBA.disconnect()
        self.ui.buttonBA.clicked.connect(self.iniciarBA)

    def iniciarTT(self):
        '''
        t_s1,t_b1,t_m1,
        cmax1,t_s2,t_b2,
        t_m2,cmax2,t_traslape,
        pw,msi,canales = (6,7)
        '''
        self.ch1_actual = int(self.ui.ch1_box_tt.value())
        vector,_ = getTrapecio_traslapado(
            self.ui.t_subidaCH1_box_tt.value(),
            self.ui.t_bajadaCH1_box_tt.value(),
            self.ui.tmeseta_ch1_box.value(),
            self.ui.current_max_ch1_box_tt.value(),
            self.ui.t_subidaCH2_box_tt.value(),
            self.ui.t_bajadaCH2_box_tt.value(),
            self.ui.tmeseta_ch2_box.value(),
            self.ui.current_max_ch2_box_tt.value(),
            self.ui.t_traslape_box.value(),
            int(self.ui.pw_box_tt.value()),
            int(self.ui.msi_box_tt.value()),
            (int(self.ui.ch1_box_tt.value()-1),int(self.ui.ch2_box_tt.value()-1))
        )
        self.programa = loop_signal(vector,self.ui.No_iter_tt.value())
        self.ui.buttonTT.setText(self._translate("MainWindow", "Parar"))
        self.ui.buttonTT.disconnect()
        self.ui.buttonTT.clicked.connect(self.programa.stop)
        self.programa.fin.connect(self.finTT)
        self.programa.stimuli.connect(self.update_canales)
        self.programa.start()
        self.ui.Status_txt.clear()
        self.ui.Status_txt.insertPlainText("Inicializado\n")
    
    def finTT(self,msj):
        self.ui.Status_txt.insertPlainText(msj)
        self.update_canvas()
        self.t1,self.t2,self.ch1,self.ch2=[],[],[],[]
        self.ui.buttonTT.setText(self._translate("MainWindow", "Iniciar"))
        self.ui.buttonTT.disconnect()
        self.ui.buttonTT.clicked.connect(self.iniciarTT)
    
    def cargarDic(self):
        self.d_vectores = load(self.ui.path.text())
        self.ui.SelectStim.clear()
        self.ui.path.clear()
        self.ui.SelectStim.addItems([self._translate("MainWindow", key) for key in self.d_vectores])
    
    def iniciarUSRMODE(self):
        key = self.ui.SelectStim.currentText()
        vector = self.d_vectores[key]
        self.ch1_actual = int(vector[0][-1]+1)
        self.programa = loop_signal(vector,self.ui.No_iter_usr_box.value())
        self.ui.button_fromfile.setText(self._translate("MainWindow", "Parar"))
        self.ui.button_fromfile.disconnect()
        self.ui.button_fromfile.clicked.connect(self.programa.stop)
        self.programa.fin.connect(self.finUSRMODE)
        self.programa.stimuli.connect(self.update_canales)
        self.programa.start()
        self.ui.Status_txt.clear()
        self.ui.Status_txt.insertPlainText("Inicializado\n")

    def finUSRMODE(self,msj):
        self.ui.Status_txt.insertPlainText(msj)
        self.update_canvas()
        self.t1,self.t2,self.ch1,self.ch2=[],[],[],[]
        self.ui.button_fromfile.setText(self._translate("MainWindow", "Iniciar"))
        self.ui.button_fromfile.disconnect()
        self.ui.button_fromfile.clicked.connect(self.iniciarUSRMODE)

    def update_canales(self,tiempo,c,canal):
        t = tiempo - self.programa.t0
        #print(canal,self.ch1_actual-1)
        if canal == self.ch1_actual-1:
            self.ch1.append(c)
            self.t1.append(t)
        else:
            self.ch2.append(c)
            self.t2.append(t)

    def update_canvas(self):
        ax = self.ui.GrafCanvas.axes[0]
        ax.clear()
        m = int()
        if len(self.ch1) != 0:
            ax.stem(self.t1,self.ch1,label = "CH1",linefmt='green',markerfmt='go')
            m = max(self.ch1)
        if len(self.ch2) != 0:
            ax.stem(self.t2,self.ch2,label = "CH2")
            m = max([m,max(self.ch2)])
        ax.set_ylim(0,m+m*.2)
        ax.legend()
        ax.grid()
        self.ui.GrafCanvas.draw()

class loop_signal(QtCore.QObject):
    fin = QtCore.pyqtSignal(str)
    stimuli = QtCore.pyqtSignal(float,float,float)
    def __init__(self,vector,repeticiones):
        super().__init__()
        self.vector = vector
        self.N = repeticiones

        #Ejecución del ciclo en un hilo distinto al del programa
        self.hilo = Thread(target=self.loop)
        self.end = Event()

        #inicializar la conexion con el estimulador y configuración
        self.t0 = time.time()
        playsound("resources/inicio.wav")
        self.c_stim = CntrlStim()
    
    def start(self):
        self.hilo.start()

    def stop(self):
        self.end.set()

    def loop(self):
        time.sleep(.5)
        self.t0 = time.time()
        for _ in range(self.N):
            Thread(target=playsound,args=("resources/sin440.wav",)).start()
            self.sendSignalQt()
            if self.end.is_set():
                self.fin.emit("Abortado")
                self.c_stim.port.close()
                self.c_stim.exitStim()
                return
        self.c_stim.port.close()
        self.c_stim.exitStim()
        self.fin.emit("Finalizado\n")
    
    def sendSignalQt(self):
        for pw,msi,c,canal in self.vector:
            #Enviar una corriente en el modo de pulso simple, el channel recibe un numero del 0 al 7
            self.c_stim.send_packet(self.c_stim.SINGLEPULSE, channel=canal, pulse_width=pw, current=c)
            self.stimuli.emit(time.time(),c,canal)
            time.sleep((msi-.8)*1e-3-pw*1e-6)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())