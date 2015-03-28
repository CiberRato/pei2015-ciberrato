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
#include "cbpanelhandler.h"

#include <iostream>
#include <qstring.h>
#include "cbparamhandler.h"
#include "cbgridhandler.h"
#include "cblabhandler.h"

using namespace std;

cbPanelHandler::cbPanelHandler(QString message)
{
	this->message = message;
}

bool cbPanelHandler::startDocument()
{
    return true;
}

bool cbPanelHandler::endDocument()
{
	return true;
}

bool cbPanelHandler::startElement(const QString&, const QString&, const QString& qName, const QXmlAttributes& attr)
{
	/* process begin tag */
	const QString &tag = qName;
	cout << "Testing: " << endl;
	cout << qName.toUtf8().constData() << endl;
	if (tag == "Start")
	{
		command.type = cbPanelCommand::START;
	}
	else if (tag == "Restart") 
	{
		command.type = cbPanelCommand::RESTART;
	}
	else if (tag == "Stop")
	{
		command.type = cbPanelCommand::STOP;
	}
	else if (tag == "DeleteRobot")
	{
		const QString &id = attr.value(QString("Id"));
		if (!id.isNull()) {
			command.type = cbPanelCommand::ROBOTDEL;
			command.robot.id = id.toInt();
		}
	}
	else if (tag == "Parameters")
	{
		cbParamHandler *paramHandler = new cbParamHandler(NULL);
		QXmlSimpleReader xmlParser;
		xmlParser.setContentHandler(paramHandler);

		QXmlInputSource data;
		data.setData(message);
		if(xmlParser.parse(data)) {
		    command.param = paramHandler->parsedParameters();
			command.type = cbPanelCommand::PARAMETERS;
		} else {
			return false;
		}
	}
	else if (tag == "Grid")
	{
		cbGridHandler *gridHandler = new cbGridHandler();
		QXmlSimpleReader xmlParser;
		xmlParser.setContentHandler(gridHandler);

		QXmlInputSource data;
		data.setData(message);
		if(xmlParser.parse(data)) {
		    command.grid = gridHandler->parsedGrid();
			command.type = cbPanelCommand::GRID;
		} else {
			return false;
		}
	}
	else if (tag == "Lab")
	{
		cbLabHandler *labHandler = new cbLabHandler();
		QXmlSimpleReader xmlParser;
		xmlParser.setContentHandler(labHandler);

		QXmlInputSource data;
		data.setData(message);
		if(xmlParser.parse(data)) {
		    command.lab = labHandler->parsedLab();
			command.type = cbPanelCommand::LAB;
		} else {
			return false;
		}
	}
	else
	{
		command.type = cbPanelCommand::UNKNOWN;
		return false;
	}
    return true;
}

bool cbPanelHandler::endElement(const QString&, const QString&, const QString& qName)
{
	//cout << "cbPanelHandler::endElement:: " << qName << endl;
	/* process end tag */
	const QString &tag = qName;
	if (tag == "Start")
	{
		if (command.type != cbPanelCommand::START)
		{
			cerr << "Missmatched end Start tag\n";
			return false;
		}
	}
	else if (tag == "Restart")
	{
		if (command.type != cbPanelCommand::RESTART)
		{
			cerr << "Missmatched end Restart tag\n";
			return false;
		}
	}
	else if (tag == "Stop")
	{
		if (command.type != cbPanelCommand::STOP)
		{
			cerr << "Missmatched end Stop tag\n";
			return false;
		}
	}
	else if (tag == "DeleteRobot")
	{
		if (command.type != cbPanelCommand::ROBOTDEL)
		{
			cerr << "Missmatched end RobotRemove tag\n";
			return false;
		}
	}
	else if (tag == "Parameters")
	{
		if (command.type != cbPanelCommand::PARAMETERS)
		{
			cerr << "Missmatched end Parameters tag\n";
			return false;
		}
	}
	else if (tag == "Grid")
	{
		if (command.type != cbPanelCommand::GRID)
		{
			cerr << "Missmatched end Grid tag\n";
			return false;
		}
	}
	else if (tag == "Lab")
	{
		if (command.type != cbPanelCommand::LAB)
		{
			cerr << "Missmatched end Lab tag\n";
			return false;
		}
	}
	else
	{
		cerr << "Unknown tag\n";
		return false;
	}
    return true;
}

void cbPanelHandler::setDocumentLocator(QXmlLocator *)
{
	return ;
}

cbPanelCommand &cbPanelHandler::Command()
{
	return command;
}

