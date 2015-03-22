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

using std::cerr;

cbPanelHandler::cbPanelHandler()
{
}
 
bool cbPanelHandler::startDocument()
{
    return true;
}

bool cbPanelHandler::endDocument()
{
	return true;
}

bool cbPanelHandler::startElement( const QString&, const QString&, const QString& qName, const QXmlAttributes& attr)
{
	//cout << "cbPanelHandler::startElement:: " << qName << endl;
	/* process begin tag */
	const QString &tag = qName;
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
	else if (tag == "Robot")
	{
		/* process attributes */
		const QString &removed = attr.value(QString("Removed"));
		if (!removed.isNull() && removed == "Yes")
		{
			command.type = cbPanelCommand::ROBOTDEL;
			command.robot.id = 0;
		}
		const QString &id = attr.value(QString("Id"));
		if (!id.isNull()) command.robot.id = id.toInt();
	}
	else
	{
		command.type = cbPanelCommand::UNKNOWN;
		return false;
	}
    return true;
}

bool cbPanelHandler::endElement( const QString&, const QString&, const QString& qName)
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
	else if (tag == "Robot")
	{
		if (command.type != cbPanelCommand::ROBOTDEL)
		{
			cerr << "Missmatched end RobotRemove tag\n";
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

