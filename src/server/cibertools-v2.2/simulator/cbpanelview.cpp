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

#include "cbpanelview.h"
#include "cbpanelhandler.h"
#include <iostream>

using namespace std;

cbPanelView::cbPanelView(cbClient * socket) : cbEntity(socket), cbPanelInterface(), cbViewInterface()
{
}

cbPanelView::~cbPanelView()
{
}


bool cbPanelView::readCommand(cbPanelCommand *command)
{
    /* look for an incoming message */
    //char xmlBuff[1024*32];
    //int xmlSize;

    //if (!hasPendingDatagrams())
    //    return false;

    QByteArray readArr, xmlBuff;
    while (strcmp((readArr = socket->read(1)).data(), "\x04") != 0) {
        if (readArr.isEmpty()) {
            cerr << "[cbReceptionist] Delimeter not found in the message, check the message sent.\n";
            return false;
        }
        xmlBuff += readArr;
    }
    /*if ((xmlSize=readDatagram(xmlBuff, 1024*32-1)) < 0)
    {
        cerr << "Error reading from Viewer Socket - " << errorString().toStdString();
        return false;
    }
    else xmlBuff[xmlSize]='\0';*/

#ifdef DEBUG_VIEW
    cerr << "cbPanel: " << xmlBuff << endl;
#endif

    /* parse xml message */
    source.setData(xmlBuff);
    cbPanelHandler *handler = new cbPanelHandler(QString(xmlBuff));
    parser.setContentHandler(handler);
    if (!parser.parse(source))
    {
        cerr << "cbPanel::Fail parsing xml view message\n";
        return false;
    }
    *command = handler->Command();
    return true;
}
