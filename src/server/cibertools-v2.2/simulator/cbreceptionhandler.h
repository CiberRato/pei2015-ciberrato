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
#ifndef _CB_RECEPTION_HANDLER_
#define _CB_RECEPTION_HANDLER_

#include <qxml.h>
#include "cbclient.h"
#include <QTcpSocket>

class QString;
class QXmlLocator;

class cbView;
class cbRobot;
class cbRobotBeacon;
class cbPanel;
class cbPanelView;

/**
 * SAX parser for registering message
 */

class cbReceptionHandler : public QXmlDefaultHandler
{
public:
	enum Type { UNKNOWN, VIEW, PANEL, PANELVIEW, ROBOT, ROBOTBEACON};
	cbReceptionHandler(QXmlSimpleReader *xmlParser, QTcpSocket *client);

    bool parse(void *data, int datasize);
    
    bool startDocument();
    bool endDocument();
    bool startElement( const QString&, const QString&, const QString& , const QXmlAttributes& );
    bool endElement( const QString&, const QString&, const QString& );
	void setDocumentLocator(QXmlLocator *);

	cbRobot *robotObject();
	cbRobotBeacon *robotBeaconObject();
	cbView *viewObject();
	cbPanel *panelObject();
    cbPanelView *panelViewObject();
	Type objectType();

private:
    QXmlInputSource xmlSource;
    QXmlSimpleReader *xmlParser;

	cbView *view;
	cbPanel *panel;
    cbPanelView *panelview;
	cbRobot *robot;
	cbRobotBeacon *robotBeacon;
	Type type;

    cbClient *client;
};                   

#endif
