/*
    This file is part of ciberRatoToolsSrc.

    Copyright (C) 2001-2014 Universidade de Aveiro

    ciberRatoToolsSrc is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    ciberRatoToolsSrc is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Foobar; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
*/

#include <iostream>
#include <stdlib.h>
#include <fstream>
#include <signal.h>

#include <QtGui>
#include <QApplication>
#include <QPushButton>
#include <QMessageBox>
#include <QLocale>

#ifndef MicWindows

#include <sys/time.h>
#include <unistd.h>
#include <netdb.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#else

#include <process.h>

#endif

#include <stdio.h>

#include <qxml.h>
#include <qstring.h>
#include <qfile.h>
#include <qvector.h>

#include "cbsimulator.h"
#include "cblab.h"
#include "cblabhandler.h"
#include "cbgridhandler.h"
#include "cbparamhandler.h"
#include "cbreceptionist.h"
#include "cbgrid.h"
#include "cbmotor.h"
#include "cbsensor.h"
#include "cbrobot.h"
#include "cbutils.h"


#include "cbsimulatorGUI.h"

#define LOG "simulation.log"

using std::cerr;


/*!
	\var simulator
	\brief The main object of the simulator.
*/
static cbSimulator simulator;


//static QXmlSimpleReader xmlParser;	// parser for xml data



/*
 * This is necessary in order the static data member becomes
 * real before the existence of any object of the class.
 */

//Noise
double  cbMotor::noise = 0.0;
double  cbCompassSensor::noise = 0.0;
double  cbBeaconSensor::noise = 0.0;
double  cbIRSensor::noise = 0.0;
double  cbGPSSensor::noiseLin = 0.5;
double  cbGPSSensor::noiseAng = 5.0;
double  cbGPSSensor::offsetX   = randUniform(0.0,1000.0);
double  cbGPSSensor::offsetY   = randUniform(0.0,1000.0);
double  cbGPSSensor::offsetDeg = 0.0;  // a different value would not be consistent with XY reference frame nor with compass

bool    cbRobot::GPSOn = true;
bool    cbRobot::GPSDirOn = false;
bool    cbRobot::scoreSensorOn = false;
bool    cbRobot::showActions = true;
bool    cbRobot::showMeasures = true;
bool    cbRobot::ignoreOthers = false;

//Scores
int     cbRobot::returnTimePenalty = 25;
int     cbRobot::arrivalTimePenalty = 100;
int     cbRobot::collisionWallPenalty = 2;
int     cbRobot::collisionRobotPenalty = 2;
int     cbRobot::targetReward = 100;
int     cbRobot::homeReward = 100;

//Requests
unsigned int    cbRobot::maxSensorsRequested = 4;

bool    cbIRSensor::sensorRequestable        = true;
bool    cbBeaconSensor::sensorRequestable    = true;
bool    cbCompassSensor::sensorRequestable   = true;
bool    cbGroundSensor::sensorRequestable    = true;
bool    cbCollisionSensor::sensorRequestable = false;
bool    cbGPSSensor::sensorRequestable       = false;

//Latencies
int     cbIRSensor::sensorLatency        =  0;
int     cbBeaconSensor::sensorLatency    =  4;
int     cbCompassSensor::sensorLatency   =  4;
int     cbGroundSensor::sensorLatency    =  0;
int     cbCollisionSensor::sensorLatency =  0;
int     cbGPSSensor::sensorLatency       =  0;

double  cbBeaconSensor::sensorAperture    = M_PI;

void CommandLineError()
{
    QMessageBox::critical(0,"Error", 
		    "SYNOPSIS: simulator [-lab file] [-grid file] [-log file] [-param file] [-port portnumber] [-showgraph id] [-gps] [-nogui]",
		    QMessageBox::Ok, Qt::NoButton, Qt::NoButton);
    exit(1);
}


/*
 * This program accepts the following command line options
 * -lab string: name of file with lab description (default, stdin);
 * -grid string: name of file with start position grid (default, stdin);
 * -log string: name of log file (default, server.log);
 * -nc real: compass noise coeficient (default, 0.0);
 * -nb real: beacon noise coeficient (default, 0.0);
 * -ni real: infrared noise coeficient (default, 0.0);
 * -nm real: motors noise coeficient (default, 0.0);
 * -st integer: simulation time, in number of cycle time units (default, 3000);
 * -ct integer: cycle time, in miliseconds (default, 75).
 */
int main(int argc, char *argv[])
{
	/* Copyright and wellcome message */
    printf(" CiberRato 2014 Simulator\n Copyright (C) 2001-2014 Universidade de Aveiro\n");
    fflush(stdout);

	/* extract option values */
	char *labFilename = 0;
	char *gridFilename = 0;
	char *paramFilename = 0;
	char *logFilename = 0;
	int port = 6000;
	bool nogui = false;

	bool showGraph=false;
	int showGraphId=0;

    //cout << "Parse command line (First Pass) ..."

    int p=1;
	while (p < argc) 
	{
        if (strcmp(argv[p], "-lab") == 0) {
            if (p+1 < argc) {
                labFilename = argv[p+1];
                p+=2;
            }
            else CommandLineError();
		}
        else if (strcmp(argv[p], "-grid") == 0) {
            if (p+1 < argc) {
                gridFilename = argv[p+1];
                p+=2;
            }
            else CommandLineError();
		}
        else if (strcmp(argv[p], "-log") == 0) {
            if (p+1 < argc) {
                logFilename = argv[p+1];
                p+=2;
            }
            else CommandLineError();
        }
        else if (strcmp(argv[p], "-param") == 0) {
            if (p+1 < argc) {
                paramFilename = argv[p+1];
                p+=2;
            }
            else CommandLineError();
		}
        else if (strcmp(argv[p], "-port") == 0)	{
            if (p+1 < argc) {
                sscanf(argv[p+1], "%d", &port);
                p+=2;
            }
            else CommandLineError();
		}
		else if (strcmp(argv[p], "-gps") == 0)	{
            // wait until second pass of command line parsing
            p+=1;
		}
		else if (strcmp(argv[p], "-showactions") == 0)	{
            // wait until second pass of command line parsing
            p+=1;
		}
        else if (strcmp(argv[p], "-showgraph") == 0)	{
            if (p+1 < argc) {
                showGraph=true;
                sscanf(argv[p+1], "%d", &showGraphId);
                p+=2;
            }
            else CommandLineError();
		}
		else if (strcmp(argv[p], "-nogui") == 0) {
			// wait until second pass of command line parsing
            p+=1;
		}
        else {
            CommandLineError();
		}
	}
	
	/* change parameteres object */
	if (paramFilename) // a parameters file is given
		simulator.changeParameters(paramFilename);

    //cout << "Parse command line (Second Pass) ..."
	// The second pass of command line arguments overrides 
    // parameters values that are defined in parameters file
    p=1;
	while (p < argc) 
	{
        if (strcmp(argv[p], "-lab") == 0) {
            if (p+1 < argc) {
                labFilename = argv[p+1];
                p+=2;
            }
            else CommandLineError();
		}
        else if (strcmp(argv[p], "-grid") == 0) {
            if (p+1 < argc) {
                gridFilename = argv[p+1];
                p+=2;
            }
            else CommandLineError();
		}
        else if (strcmp(argv[p], "-log") == 0) {
            if (p+1 < argc) {
                logFilename = argv[p+1];
                p+=2;
            }
            else CommandLineError();
		}
        else if (strcmp(argv[p], "-param") == 0) {
            if (p+1 < argc) {
                paramFilename = argv[p+1];
                p+=2;
            }
            else CommandLineError();
		}
        else if (strcmp(argv[p], "-port") == 0)	{
            if (p+1 < argc) {
                sscanf(argv[p+1], "%d", &port);
                p+=2;
            }
            else CommandLineError();
		}
        else if (strcmp(argv[p], "-gps") == 0)	{
            cbRobot::GPSOn = true;
            simulator.setGPS(true);
            p+=1;
		}
        else if (strcmp(argv[p], "-showactions") == 0)	{
            cbRobot::showActions=true;
            p+=1;
		}
        else if (strcmp(argv[p], "-showgraph") == 0)	{
            if (p+1 < argc) {
                showGraph=true;
                sscanf(argv[p+1], "%d", &showGraphId);
                p+=2;
            }
            else CommandLineError();
		}
		else if (strcmp(argv[p], "-nogui") == 0) {
			nogui = true;
			p+=1;
		}
        else {
            CommandLineError();
		}
	}
	//cout << " done.\n";

	QApplication app(argc, argv, !nogui);

    setlocale(LC_ALL,"C");
    QLocale::setDefault(QLocale::c());

	/* change lab object */
	if (labFilename) // a lab file is given
		simulator.changeLab(labFilename);

	/* change grid object */
	if (gridFilename) // a grid file is given
		simulator.changeGrid(gridFilename);


    if(logFilename)
        simulator.setLogFilename(logFilename);

	simulator.setReceptionistAt(port);

    simulator.buildGraph();
    simulator.setDistMaxFromGridToTarget();

    if(showGraph) {
        simulator.showGraph(showGraphId);
        if(simulator.labView)
            simulator.labView->show();
	}
	/* preparing the random generator */
#ifndef MicWindows
	srand(getpid());
#else
	srand(_getpid());
#endif
    /* start simulator timer */
	simulator.startTimer();

	cbSimulatorGUI * gui = NULL;
    if (!nogui) {
		gui = new cbSimulatorGUI(&simulator);
		simulator.setGUI(gui);
        
		//gui.setMaximumSize(gui.size());
		//gui.setMinimumSize(gui.size());
		gui->show();
    }
    app.exec();

    delete gui;
	return 0;
}
