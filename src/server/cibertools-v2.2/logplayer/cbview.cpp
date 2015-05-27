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

#include "cbview.h"

#include <QUdpSocket>
#include <QHostAddress>

#include <iostream>

using std::cerr;

cbView::cbView(cbClient * socket) : cbEntity(socket)
{
}

cbView::~cbView()
{
}


/*!
	Try to read a command from the incoming socket.
	If one, fill in the area pointed to by command and
	return TRUE.
	Otherwise return FALSE.
*/
bool cbView::readCommand(cbCommand *command)
{
    QByteArray readArr, xmlBuff;
    while (strcmp((readArr = socket->read(1)).data(), "\x04") != 0) {
        if (readArr.isEmpty()) {
            cerr << "[cbReceptionist] Delimeter not found in the message, check the message sent.\n";
            return false;
        }
        xmlBuff += readArr;
    }

#ifdef DEBUG_VIEW
    cerr << "cbView: " << xmlBuff << endl;
#endif

    /* parse xml message */
    source.setData(xmlBuff);
    cbPanelHandler *handler = new cbPanelHandler(QString(xmlBuff));
    parser.setContentHandler(handler);
    if (!parser.parse(source))
    {
        cerr << "cbView::Fail parsing xml view message\n";
        return false;
    }
    *command = handler->Command();
    return true;
}


