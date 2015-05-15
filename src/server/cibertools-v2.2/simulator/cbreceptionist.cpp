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
/*
	cbReceptionist

*/

#include "cbreceptionist.h"

#include "cbreceptionform.h"
#include "cbreceptionhandler.h"
#include "cbserver.h"

#include <QHostAddress>
#include <QString>
#include <QMessageBox>
#include <qxml.h>

#include <string.h>
#include <stdlib.h>

using std::cerr;
using std::cout;

/*!
	Create socket and bind it with machine address and given port.
	Set the socket non-blocking.
*/
cbReceptionist::cbReceptionist() {
    /*QHostAddress address;
    address.setAddress(QString("0.0.0.0"));     // this way any address is accepted
	*//* bind local address */
	//cout.form(" binding to address %s and port %hd...\n", "0.0.0.0", port);
    /*if (!bind(address, port, QUdpSocket::ShareAddress))
    {
        cerr << " Couldn't open socket at port " << port << "\n";
        status = false;
        return;
    }*/

	/* make initialization */
	xmlParser = new QXmlSimpleReader;
	status = true;
}

/*!	
	Does nothing.
*/
cbReceptionist::~cbReceptionist()
{
}

/*!
	Returns true if internal status is bad, and returns false if it is good.
*/
bool cbReceptionist::bad(void)
{
	return status == false;
}


/*!
	Set the xml parser.
*/
/**
void cbReceptionist::setXmlParser(QXmlSimpleReader *parser)
{
	xmlParser = parser;
	
}
**/


///*!
//	Set the xml source.
//*/
//void cbReceptionist::setXmlSource(QXmlInputSource *source)
//{
//	xmlSource = source;
//}
//
//
/*!
	Check input port for an incoming xml message.
	If one, parse it, fill in the check-in form and return true;
	Otherwise returns false.
*/
bool cbReceptionist::CheckIn(QTcpSocket* client)
{
    //cout << "Entering checkIn\n";
	/* check if parser is set */
	int datasize;
	if (xmlParser == 0) 
	{
        cerr << "Parser was not setup\n";
        QMessageBox::critical(0,"Error",
                              "Error in parser",
                              QMessageBox::Ok, Qt::NoButton, Qt::NoButton);
        exit (1);
	}
	
	/* look for an incoming message */
    //if (!hasPendingDatagrams())
    //    return false;

	datasize = client->bytesAvailable();
    client->read(xmlBuff, client->bytesAvailable());

    /*if ((datasize=readDatagram(xmlBuff, XMLMAX-1, &form.addr, &form.port)) < 0)
    {
        cerr << "Error no. " << error() << " reading from the socket!\n";
        QMessageBox::critical(0,"Error",
                              QString("Error no. ")+QString::number(error())+ " reading from socket",
                              QMessageBox::Ok, Qt::NoButton, Qt::NoButton);
		return false;
	}
	else xmlBuff[datasize]='\0';*/

    //cout << xmlBuff << endl;

	/* parse xml message */
	cbReceptionHandler handler(xmlParser, client);

	if (!handler.parse(xmlBuff,datasize))
	{
		cerr << "Fail parsing xml message\n" << xmlBuff << "\n";
		return false;
	}

	//xmlParser->setContentHandler(&handler);
	//xmlSource.setData(xmlBuff);
	//if (!xmlParser->parse(xmlSource))
	//{
	//	cerr.form("Fail parsing xml message\n");
	//	return false;
	//}
	
    /* process request */

	switch (handler.objectType())
	{
		case cbReceptionHandler::ROBOT:
			form.type = cbClientForm::ROBOT;
			//form.client.robot = (cbRobot*) client; 
			cout << "Robot is requesting registration\n";
			break;
		case cbReceptionHandler::ROBOTBEACON:
			form.type = cbClientForm::ROBOTBEACON;
			//form.client.robotBeacon = (cbRobotBeacon*) client; 
			cout << "RobotBeacon is requesting registration\n";
			break;
		case cbReceptionHandler::VIEW:
			form.type = cbClientForm::VIEW;
			//form.client.view = (cbView*) client; //handler.viewObject();
            cout << "Viewer is requesting registration\n";
			break;
		case cbReceptionHandler::PANEL:
			form.type = cbClientForm::PANEL;
			//form.client.panel = (cbPanel*) client; 
			cout << "Panel is requesting registration\n";
			break;
		case cbReceptionHandler::PANELVIEW:
			form.type = cbClientForm::PANELVIEW;
			//form.client.panelview = (cbPanelView*) client; 
			cout << "PanelView is requesting registration\n";
			break;
		default:
			form.type = cbClientForm::UNKNOWN;
			break;
	}
	return true;
}

/*!
	Returns the last filled check-in (client) form.
*/
cbClientForm &cbReceptionist::Form()
{
	return form;
}
