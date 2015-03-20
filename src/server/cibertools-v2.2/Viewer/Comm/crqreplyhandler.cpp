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

#include "crqreplyhandler.h"
#include <iostream>
#include <stdlib.h>
#include <qstring.h>

using namespace std;

bool CRQReplyHandler::startDocument()
{
	replyObject = 0;
    type = UNKNOWN;
    return TRUE;
}

/*---------------------------------------------------------------------------*/
bool CRQReplyHandler::startElement( const QString&, const QString&, 
  const QString& qName, const QXmlAttributes& attr)
{
	/* process begin tag */
    const QString &tag = qName;
    switch (type) {
        case UNKNOWN:
            if( tag == "Reply" )
            {
                replyObject = new CRReply; 
                // process attributes
                const QString status = attr.value( QString( "Status" ));
                if ( !status.isNull() )
                {
                    if( status == "Ok" )
                        replyObject->status = true;
                    else
                        replyObject->status = false;
                }
            } else if ( tag == "Parameters") {
                type = PARAMETERS;
                replyObject->parameters = new CRParameters();

                const QString cycleTime = attr.value( QString( "CycleTime" ));
                if( !cycleTime.isNull() )
                    replyObject->parameters->cycleTime = cycleTime.toUInt();

                const QString simTime = attr.value( QString( "SimTime" ));
                if( !simTime.isNull() )
                    replyObject->parameters->simTime = simTime.toUInt();

                const QString compassTime = attr.value (QString( "CompassTime" ));
                if( !compassTime.isNull() )
                    replyObject->parameters->compassTime = compassTime.toUInt();

                const QString obstacleNoise = attr.value(QString("ObstacleNoise"));
                if( !obstacleNoise.isNull() )
                    replyObject->parameters->obstacleNoise =
                      obstacleNoise.toDouble();

                const QString motorsNoise = attr.value (QString( "MotorsNoise" ));
                if( !motorsNoise.isNull() )
                    replyObject->parameters->motorsNoise = motorsNoise.toDouble();
            }
            else if ( tag == "Grid" )
            {
                type = GRID;    //Next time startElement will process one GRID
                replyObject->grid = new CRGrid();
            }
            else if (tag == "Lab") {
                type = LAB;
                replyObject->lab = new CRLab();
                // process attributes
                const QString name = attr.value(QString("Name"));
                if( !name.isNull() )
                    replyObject->lab->setName( name.toAscii() );

                const QString width = attr.value(QString("Width"));
                if( !width.isNull() )
                    replyObject->lab->setWidth( width.toFloat() );

                const QString height = attr.value(QString("Height"));
                if( !height.isNull() )
                    replyObject->lab->setHeight( height.toFloat() );
            } 
            else {
                return false;
            }
            break;
        case PARAMETERS:
            break;
        case GRID:
            if( tag == "Position" )
            {
                type = POSITION;
                gridElement = new CRGridElement();
                // Process attributs
                const QString x = attr.value(QString("X"));
                if (!x.isNull())
                    gridElement->position.setX( x.toFloat() );

                const QString y = attr.value(QString("Y"));
                if (!y.isNull())
                    gridElement->position.setY( y.toFloat() );

                const QString dir = attr.value(QString("Dir"));
                if (!dir.isNull())
                    gridElement->direction = dir.toFloat();

                replyObject->grid->addPosition( gridElement ); // Add one position to the grid
            } 
            else {
                return false;
            }
            break;
        case LAB:
            if (tag == "Wall")
            {
                type = WALL;
                wall = new CRWall;
                /* process attributes */
                const QString height = attr.value(QString("Height"));
                if (!height.isNull())
                    wall->setWallHeight( height.toFloat() );
            }
            else if (tag == "Beacon")
            {
                type = BEACON;
                vertice = new CRVertice;
                beacon = new CRBeacon( *vertice );
                /* process attributes */
                const QString x = attr.value(QString("X"));
                if (!x.isNull())
                    vertice->setX( x.toFloat() );

                const QString y = attr.value(QString("Y"));
                if (!y.isNull())
                    vertice->setY( y.toFloat() );

                const QString height = attr.value(QString("Height"));
                if (!height.isNull())
                    replyObject->lab->addBeacon( *vertice, height.toFloat() );
                else
                    replyObject->lab->addBeacon( *vertice );
            }

            else if (tag == "Target")
            {
                type = TARGET;
                target = new CRTarget;
                vertice = new CRVertice;
                /* process attributes */
                const QString x = attr.value(QString("X"));
                if (!x.isNull())
                    vertice->setX( x.toFloat() );

                const QString y = attr.value(QString("Y"));
                if (!y.isNull())
                    vertice->setY( y.toFloat() );

                const QString radius = attr.value(QString("Radius"));
                if (!radius.isNull())
                    replyObject->lab->addTarget( *vertice, radius.toFloat() );
                else
                    replyObject->lab->addTarget( *vertice );
            }
            else {
                return false;
            }
            break;
        case WALL:
            if (tag == "Corner") {
                type = CORNER;
                vertice = new CRVertice;
                // process attributes
                const QString x = attr.value(QString("X"));
                if (!x.isNull())
                    vertice->setX(x.toFloat());

                const QString y = attr.value(QString("Y"));
                if (!y.isNull())
                    vertice->setY(y.toFloat());
                wall->addCorner(*vertice);
            }
            else {
                return false;
            }
            break;
    }
    return true;
}
bool CRQReplyHandler::endElement( const QString&, const QString&, const
                                QString& qName) {
    const QString &tag = qName;
    switch (type)
    {
        case UNKNOWN:
            break;
        case PARAMETERS:
        case LAB:
        case GRID:
            type = UNKNOWN;
            break;
        case BEACON:
        case TARGET:
            type = LAB;
            break;
        case WALL:
            replyObject->lab->addWall(wall);
            type = LAB;
            break;
        case CORNER:
            type = WALL;
            break;
        case POSITION:
            type = GRID;
            break;
    }
    return true;
}
/*---------------------------------------------------------------------------*/
bool CRQReplyHandler::endDocument()
{
    return true;
}

/*---------------------------------------------------------------------------*/
void CRQReplyHandler::setDocumentLocator( QXmlLocator * )
{

}

/*---------------------------------------------------------------------------*/
CRReply * CRQReplyHandler::reply()
{
	return replyObject;
}

CRQReplyHandler::Type CRQReplyHandler::objectType()
{
    return type;
}