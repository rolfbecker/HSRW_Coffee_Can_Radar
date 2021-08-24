'''
R. Becker, 2021-08-24
HSRW DIY Radar: Data Receiver, FFT, and Realtime Plotting
This program is used to receive data from a teensy via vircual com port at high serial baud rate.
The data is expected to be arranged in three columns. Each column contains a sampled signal.
PYQT is used for realtime graphics because it is extremely fast, faster than other solutions I (rb) know.
The COM port in the code is hard coded.
'''
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from pyqtgraph.ptime import time
import serial as ser

CHUNKSZ = 4096 # NUMBERS
#CHUNKSZ = 8192 # NUMBERS
fs = 100000 # Hz, depending on Teensy prog.
#sRate = 100000 # 100KHz, depending on Teensy prog.
app = QtGui.QApplication([])

hanwin = np.hanning(CHUNKSZ)

win = pg.GraphicsWindow(title="Basic plotting examples")
win.resize(1000,600)
win.setWindowTitle('DIY Teensy Radar')

p1 = win.addPlot(title='sample')
#p1.setRange(QtCore.QRectF(0, -10, CHUNKSZ, 70010)) 
p1.setRange(QtCore.QRectF(0, -33000, CHUNKSZ, 33000)) 
p1.setLabel('bottom', 'Index', units='B')
curve1 = p1.plot()

win.nextRow()

p2 = win.addPlot(title='FFT')
p2.setRange(QtCore.QRectF(0, -10, CHUNKSZ, 100)) 
p2.setRange(QtCore.QRectF(0, -10, 1000, 100)) # 0 Hz, -10 dB, 100 Points, 100 dB
#p2.setRange(QtCore.QRectF(0, -10, fs, 100)) # 0 Hz, -10 dB, 100 Points, 100 dB
#p2.setRange(QtCore.QRectF(0, -10, CHUNKSZ/10, 3000))
fScale = np.linspace(0 , 0.5*fs, CHUNKSZ/2+1) # the fft gives you 2048+1 points back if you pass 4096 to it.
#print fScale
#print len(fScale)
#exit()
curve2 = p2.plot()

#       # prepare window for later use
#        self.win = np.hanning(CHUNKSZ)
#        self.show()
#
#    def update(self, chunk):
#        # normalized, windowed frequencies in data chunk
#        spec = np.fft.rfft(chunk*self.win) / CHUNKSZ
#        # get magnitude 
#        psd = abs(spec)
#        # convert to dB scale
#        psd = 20 * np.log10(psd)


#curve.setFillBrush((0, 0, 100, 100))
#curve.setFillLevel(0)

#lr = pg.LinearRegionItem([100, 4900])
#p.addItem(lr)

#data = np.random.normal(size=(50,5000))
#ptr = 0

port = ser.Serial('COM72')

lastTime = time()
fps = None
def update():
    global curve1, curve2, data, p, lastTime, fps, hanwin, fScale
    data = np.fromstring(port.read(2*CHUNKSZ), 'uint16')
#    print type(data)
#    exit()
    data = 1.0 * data - 2**15
    print "len(data) =" , len(data)
    spec = np.fft.rfft(data*hanwin) / CHUNKSZ
    print "len(spec) =" , len(spec)
    # get magnitude 
    psd = abs(spec)
    # convert to dB scale
    psd = 20 * np.log10(psd)	
    curve1.setData(data)
#    curve2.setData(x = fScale[0:100], y = psd[0:100]) # FFT data
    curve2.setData(x = fScale, y = psd) # FFT data
    now = time()
    dt = now - lastTime
    lastTime = now
    if fps is None:
        fps = 1.0/dt
    else:
        s = np.clip(dt*3., 0, 1)
        fps = fps * (1-s) + (1.0/dt) * s
    p1.setTitle('%0.2f fps' % fps)
    app.processEvents()  ## force complete redraw for every plot

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(0)
    


## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
