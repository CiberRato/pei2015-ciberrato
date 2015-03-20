/*
    This file is part of ciberRatoToolsSrc.

    Copyright (C) 2001-2011 Universidade de Aveiro

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

#include "crqcommhandler.h"
#include <iostream>
#include <QString>

bool CRQCommHandler::startDocument()
{
	// Initialize all elements with null
	robot = NULL;
	type = UNKNOWN;

    return TRUE;
}

bool CRQCommHandler::endDocument()
{
	return TRUE;
}

bool CRQCommHandler::startElement( const QString&, const QString&,
                                   const QString& qName,
                                   const QXmlAttributes& attr)
{
    
    const QString &tag = qName;
	switch (type) { 	//Type defined in .h as enum.
        case UNKNOWN:
			// process begin tag 
            if ( tag == "LogInfo" ) {
            	type = LOGINFO;
            } else if( tag == "Restart" ) {
            	// TODO
            } else {
        		return false;
            }
            break;
        case LOGINFO:
			if(tag == "Robot") {
                type = ROBOT;  //Next time startElement will process one ROBOT
                robot = new CRRobot();
                // process attributs
                const QString name = attr.value( QString( "Name" ) );
                if( !name.isNull() )
                    robot->setName( name.toAscii() );

                const QString id = attr.value( QString( "Id" ) );
                if( !id.isNull() )
                    robot->setId( id.toInt() );
                const QString state =  attr.value( QString( "State" ) );
                if( !state.isNull() )
                {
                    if (state == "Stopped" )
                        robot->setState( CRRobot::STOPPED );

                    else if (state == "Running" )
                        robot->setState( CRRobot::RUNNING );

                    else if (state == "Waiting" )
                        robot->setState( CRRobot::WAITINGOTHERS );

                    else if (state == "Removed" )
                        robot->setState( CRRobot::REMOVED );

                    else if (state == "Finished" )
                        robot->setState( CRRobot::FINISHED );

                    else if (state == "Returning" )
                        robot->setState( CRRobot::RETURNING );
                }
            } else {
                return false;
            }
            break;
		case ROBOT:  // if received element was one 
			if( tag == "Pos" )
            {
            	type = POSITION;
                const QString x = attr.value( QString( "X" ));
                if (!x.isNull())
                    robot->setX( x.toFloat() );

                const QString y = attr.value(QString("Y"));
                if (!y.isNull())
                    robot->setY( y.toFloat() );

                const QString dir = attr.value(QString("Dir"));
                if (!dir.isNull())
                    robot->setDirection( dir.toFloat() );
            } else if (tag == "Scores") {
            	type = SCORES;
            	const QString score = attr.value( QString( "Score" ) );
                if( !score.isNull() )
                    robot->setScore( score.toInt() );

                const QString collisions =  attr.value( QString( "Collisions" ) );
                if( !collisions.isNull() )
                    robot->setCollisions( collisions.toInt() );            

                const QString arrivalTime =  attr.value( QString( "ArrivalTime" ) );
                if( !arrivalTime.isNull() )
                    robot->setArrivalTime( arrivalTime.toInt() );

                const QString returnTime =  attr.value( QString( "ReturningTime" ) );
                if( !returnTime.isNull() )
                    robot->setReturnTime( returnTime.toInt() );
            } else if (tag == "Action") {
            	type = ACTION;
            	// Ignoring actions, viewer doesn't use it at the moment
            } else if (tag == "Measures") {
            	type = MEASURES;

                const QString time =  attr.value( QString( "Time" ) );
                if( !time.isNull() )
                    robot->setCurrentTime( time.toInt() );
            } else {
            	return false;
            }
			break;
		case MEASURES:
			if (tag == "Sensors") {
				type = SENSORS;

				const QString collision =  attr.value( QString( "Collision" ) );
                if( !collision.isNull() )
                    robot->setCollision( collision.toAscii() );
			} else if (tag == "Leds") {
				type = LEDS;
			} else if (tag == "Buttons") {
				type = BUTTONS;
			} else {
				return false;
			}
			break;
		case SENSORS:
			if (tag == "IRSensor") {
				type = IRSENSOR;
				// Viewer is not using sensors at the moment
			} else if (tag == "BeaconSensor") {	
				type = BEACONSENSOR;
				// Viewer doesn't use this sensor at the moment
			} else if (tag == "GPS") {
				type = GPS;
				// Viewer doesn't use this sensor at the moment
			} else {
				return false;
			}
			break;
	}
    return true;

}

bool CRQCommHandler::endElement( const QString&, const QString&, const
								QString& qName) {
        const QString &tag = qName;
    switch (type)
    {
        case 	UNKNOWN:
        	break;
        case 	RESTART:
        		LOGINFO:
            type = UNKNOWN;
            break;
        case 	ROBOT:
            type = LOGINFO;
            break;
        case 	POSITION:
        		SCORES:
        		ACTION:
        		MEASURES:
            type = ROBOT;
            break;
        case 	SENSORS:
        		LEDS:
        		BUTTONS:
            type = MEASURES;
            break;
        case 	IRSENSOR:
        		BEACONSENSOR:
        		GPS:
            type = SENSORS;
            break;
    }
    return true;
}

CRRobot * CRQCommHandler::getRobot( void )
{
	return robot;
}

void CRQCommHandler::setDocumentLocator(QXmlLocator *)
{

}

CRQCommHandler::Type CRQCommHandler::objectType()
{
	return type;
}

