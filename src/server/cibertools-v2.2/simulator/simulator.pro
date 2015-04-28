TEMPLATE    = app
CONFIG      += qt warn_on release thread
#CONFIG     += qt warn_on debug thread
QMAKE_CXXFLAGS     += -std=c++11

win32 {
        DEFINES += MicWindows
        LIBS    += -lws2_32 
}

HEADERS = \
    cbactionhandler.h cbbeacon.h cbbutton.h cbclient.h\
    cbgrid.h cbgridhandler.h cblab.h cblabhandler.h\
    cbmotor.h cbpanel.h cbparameters.h cbparamhandler.h\
    cbpoint.h cbposition.h cbreceptionform.h cbreceptionhandler.h\
    cbreceptionist.h cbrobot.h cbrobotaction.h cbsensor.h\
    cbsimulator.h cbtarget.h cbview.h \
    cbwall.h cbgraph.h cbrobotbeacon.h \
    cbutils.h cbparamdialog.h cbsimulatorGUI.h cbcontrolpanel.h \
    cbmanagerobots.h cbpanelhandler.h cbpanelcommand.h \
    cbrobotinfo.h cbpanelview.h \
    cblabdialog.h

SOURCES = \
    cbactionhandler.cpp cbbeacon.cpp cbbutton.cpp cbclient.cpp\
    cbgrid.cpp cbgridhandler.cpp cblab.cpp cblabhandler.cpp\
    cbmotor.cpp cbpanel.cpp cbparameters.cpp cbparamhandler.cpp\
    cbpoint.cpp cbposition.cpp cbreceptionhandler.cpp cbreceptionist.cpp\
    cbrobot.cpp cbrobotaction.cpp cbsensor.cpp \
    cbsimulator.cpp cbtarget.cpp cbview.cpp \
    cbwall.cpp simulator.cpp cbgraph.cpp cbrobotbeacon.cpp\
    cbutils.cpp cbparamdialog.cpp cbsimulatorGUI.cpp cbcontrolpanel.cpp \
    cbmanagerobots.cpp cbpanelhandler.cpp \
    cbrobotinfo.cpp cbpanelview.cpp \
    cblabdialog.cpp

TARGET  = simulator
QT      += network  xml

FORMS   += \
    cbsimulatorGUI.ui \
    cbcontrolpanel.ui \
    cbmanagerobots.ui \
    cbparamdialogbase.ui \
    cbrobotinfo.ui \
    cblabdialog.ui

RESOURCES   += \
    default.qrc
