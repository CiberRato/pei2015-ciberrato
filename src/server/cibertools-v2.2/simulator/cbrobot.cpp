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

#include "cbrobot.h"
#include "cbsensor.h"
#include "cbtarget.h"
#include "cbsimulator.h"
#include "cblab.h"
#include "cbgraph.h"

#include <iostream>
#include <math.h>
#include <stdlib.h>
#include <QTime>

#include <QTextEdit>

using std::cerr;
using std::cout;

//#define DEBUG_ROBOT

// enum State and StrState (in cbrobot.cpp) must be compatible!!!
static const char *StrState[] =
{
    "Stopped", "Running", "Waiting", "Returning", "Finished", "Removed"
};

cbRobot::cbRobot(cbClient *client, const double irSensorAngle[]) : cbEntity(client)
{
	int i;

	collisionSensor = new cbCollisionSensor(this, "Collision");
	sensors.push_back(collisionSensor);

	collisionSensor->setRequestable(false);

	collisionSensor->setRequestable(cbCollisionSensor::sensorRequestable); 
	collisionSensor->setFifoLatency(cbCollisionSensor::sensorLatency);

	groundSensor    = new cbGroundSensor(this, "Ground");
	sensors.push_back(groundSensor);

	groundSensor->setRequestable(cbGroundSensor::sensorRequestable); 
	groundSensor->setFifoLatency(cbGroundSensor::sensorLatency);

	compassSensor   = new cbCompassSensor(this, "Compass");
	sensors.push_back(compassSensor);

	compassSensor->setRequestable(cbCompassSensor::sensorRequestable); 
	compassSensor->setFifoLatency(cbCompassSensor::sensorLatency);

	/* init IR sensor relative positions */
	for(i=0; i < NUM_IR_SENSORS ; i++) {
	   irSensors[i] = new cbIRSensor(this, QString("IRSensor") + QString::number(i));
	   sensors.push_back(irSensors[i]);

	   irSensors[i]->setRequestable(cbIRSensor::sensorRequestable); 
	   irSensors[i]->setFifoLatency(cbIRSensor::sensorLatency);

	   irSensors[i]->setPosition(ROBOT_RADIUS, irSensorAngle[i]);
	}

	GPSOn = true;
	GPSDirOn = false;
	GPSSensor   = new cbGPSSensor(this, "GPS");
	sensors.push_back(GPSSensor);

    GPSSensor->setRequestable(cbGPSSensor::sensorRequestable);
	GPSSensor->setFifoLatency(cbGPSSensor::sensorLatency);

    simulator = 0;
    name = 0;
	id = 0;
	score = 0;
	scorePenalties=0;
	arrivalTime=0;
	startReturningTime=0;
	returningTime=0;
	distAtArrival=0.0;
	distGridToBeacon=0.0;
	distHomeToTarget=0.0;

    //collision = false;
    collisionWall = false;
    collisionRobot = false;
	collisionPrevCycle = false;
	collisionCount = 0;

	_state = STOPPED;
	_unstoppedState = RUNNING;
	removed=false;

	endLed = false;
    returningLed=false;
    visitingLed=false;
    waitingSync=false;

	resetReceivedFlags();

	vel=0.0;
	failedSyncs = 0;
}

cbRobot::~cbRobot()
{
}

void cbRobot::setName(const char *nm)
{
	name = strdup(nm);
}

const char *cbRobot::Name()
{
	return name;
}

void cbRobot::setId(unsigned int theId)
{
	id = theId;
}

unsigned int cbRobot::Id()
{
	return id;
} 

const char *cbRobot::curStateAsString()
{
    return StrState[state()];
}

void cbRobot::setSimulator(cbSimulator *s)
{
	simulator = s; 

	// Set the number of beacon sensors
	beaconSensors.resize(simulator->Lab()->nBeacons());
	for(unsigned int b=0; b<beaconSensors.size();b++) {
		beaconSensors[b] = new cbBeaconSensor(this, QString("Beacon")+QString::number(b));
		sensors.push_back(beaconSensors[b]);

		beaconSensors[b]->setBeaconToFollow(b);
        beaconSensors[b]->setFifoLatency(cbBeaconSensor::sensorLatency);
        beaconSensors[b]->setRequestable(cbBeaconSensor::sensorRequestable);

	}

	//set the number of visited target flags and initialize
	targetVisited.resize(simulator->Lab()->nTargets(), false);

    //scorePenalties = 100 + 100 * simulator->Lab()->nTargets(); //100 for each target area + 100 for returning COMPETITIVE
    scorePenalties = targetReward * (simulator->Lab()->nTargets() - 1) + homeReward; // COOPERATIVE
	
}

void cbRobot::setIRSensorAngle(unsigned int irId, double irAngle)
{
	irSensors[irId]->setPosition(ROBOT_RADIUS, irAngle);
}

void cbRobot::setLeftMotor(double p)
{
    recLeftMotor=true;

	leftMotor.setInPower(p);
}

void cbRobot::setRightMotor(double p)
{
    recRightMotor=true;

	rightMotor.setInPower(p);
}

void cbRobot::setReturningLed(bool l)
{ 
    recReturningLed=true;

    returningLed=l;
}

void cbRobot::setVisitingLed(bool l)
{ 
    recVisitingLed=true;

    visitingLed=l;
}

void cbRobot::setSayMessage(QString msg)
{ 
    if(msg.length()<=100)
        sayMessage=msg;
}

QString cbRobot::getSayMessage(void)
{ 
    return sayMessage;
}

void cbRobot::resetReceivedFlags(void)
{ 
    recLeftMotor=recRightMotor=recVisitingLed=recReturningLed=recEndLed=false;
    sayMessage="";
}

void cbRobot::resetRequestedSensors(void)
{ 
	unsigned int s;
	for (s = 0; s < sensors.size(); s++ )
		sensors[s]->requested = false;
	nSensorsRequested = 0;
}

void cbRobot::requestSensor(QString sensorStrId)
{ 
	unsigned int s;

	if (nSensorsRequested == maxSensorsRequested) {
		cerr << "Robot " << id << " trying to request more sensors than permitted\n";
		return;	
	}

	for (s = 0; s < sensors.size(); s++ ) {
		if ( sensors[s]->getStrId() == sensorStrId ) {
            sensors[s]->requested = true;
            nSensorsRequested++;
		    break;
		}
	}

    if(s==sensors.size())
        cerr << "Robot " << id << " requested unrecognized sensor (" << sensorStrId.toStdString() << ")\n";
}

void cbRobot::incrementFailedSyncs() 
{
	failedSyncs++;
}
unsigned int cbRobot::getNumberFailedSyncs() 
{
	return failedSyncs;
}
void cbRobot::changeActiveState()
{
	if (_state == RUNNING) _state = STOPPED;
	else if (_state == STOPPED) _state = RUNNING;
}

/*!
	Try to read an action from the incoming socket.
	If one, fill in the area pointed to by action and
	return TRUE.
	Otherwise return FALSE.
*/
bool cbRobot::readAction(cbRobotAction *action)
{
    QByteArray read = socket->readAll();
    QList<QByteArray> data = read.split('\x04');
    QByteArray datagram = QByteArray("<XML>");
    for (int i = 0; i < data.length() - 1; i++) {
    	datagram += data.at(i);
    }
    old = data.at(data.length()-1);
    datagram += QByteArray("</XML>");

#ifdef DEBUG_ROBOT
	cerr << "cbRobot: " << datagram.data() << "\n";
#endif
	//cerr << read.data() << " : " << datagram.data() << "\n";
    //if (showActions)
    //    simulator->GUI()->writeOnBoard(QString(name) + " : " + datagram, (int) id, 1);

	/* parse xml message */
	QXmlSimpleReader parser;
    QXmlInputSource source;
    parser.setContentHandler(&handler);
    source.setData(datagram);
	if (!parser.parse(source))
	{
        cerr << "cbRobot::Fail parsing xml action message: \"" << datagram.constData() << "\"\n";
        simulator->GUI()->appendMessage( "cbRobot: Fail parsing xml action message:" , true);
        simulator->GUI()->appendMessage( QString(" \"")+datagram.constData()+"\"" , true);

		return false;
	}
	
	*action = handler.parsedAction();
	return true;
}

/*!
	Compute next position for robot.
*/
void cbRobot::computeNextPosition()
{
	if (_state == REMOVED) return;

	vel = (rightMotor.outPower() + leftMotor.outPower()) / 2.0;
	double rot = (rightMotor.lastOutPower() - leftMotor.lastOutPower()) / (2.0 * ROBOT_RADIUS); // outPower should be called only once per cycle

	double theta = curPos.Direction();
    /* a direc��o angular do robot
     * � dada em rela��o ao eixo dos xx. */
	double x = curPos.X() + vel * cos(theta);
	double y = curPos.Y() + vel * sin(theta);
	theta += rot;
	if (theta > M_PI) theta -= (2.0*M_PI);
	else if (theta < -M_PI) theta += (2.0*M_PI);

	nextPos.set(x,y,theta);
}

/*!
	Commit next position for robot.
	If robot is a colliding robot only angular position
	is changed.
	Otherwise next position becomes current.
*/
void cbRobot::commitNextPosition()
{
	if(blocked()) return;   // stopped or finished or removed 
    //if (collision)
    if (hasCollide())
	{
        curPos.setRadianDirection(nextPos.radianDirection());
	}
	else
	{
		curPos = nextPos;
	}
}

bool cbRobot::isOnTarget(int &targId) 
{ 
	for(unsigned int t=0; t<simulator->Lab()->nTargets(); t++) {
		if(simulator->Lab()->Target(t)->contains(curPos.Coord(),ROBOT_RADIUS)) {
			targId=t;
			return true;
		}
	}
	return false;
}

int cbRobot::targetAtPos(void) 
{ 
	for(unsigned int t=0; t<simulator->Lab()->nTargets(); t++) {
		if(simulator->Lab()->Target(t)->contains(curPos.Coord(),ROBOT_RADIUS)) {
			return t;
		}
	}
	return -1;
}

bool cbRobot::visitedAllTargets(void) 
{
	for(unsigned int t=0; t<simulator->Lab()->nTargets(); t++) {
		if(!targetVisited[t]) return false;
	}
	return true;
}

int cbRobot::nVisitedTargets(void) 
{
	int count=0;
	for(unsigned int t=0; t<simulator->Lab()->nTargets(); t++) {
		if(targetVisited[t]) count++;
	}
	return count;
}

/*!
	Determine if robot is moving towards the given point.
	Return TRUE if so, and FALSE otherwise.
*/
bool cbRobot::isMovingTowards(cbPoint &p)
{
	cbPoint &c = Center();
	/* return false if robot doesn't move */
	if (c == p) return false;

	/* determine angular deviation */
	double alpha = atan2(p.y-c.y, p.x-c.x);
	alpha = fabs(alpha - curPos.radianDirection());

	/* return TRUE if deviation lower than PI/2 */
	if(vel>0)
	    return alpha < M_PI/2.0 || alpha > 3.0*M_PI/2.0;
	else if(vel<0)
	    return alpha > M_PI/2.0 && alpha < 3.0*M_PI/2.0;
	else {
	   return false; //vel=0;
	}
}

/*!
	Update robot state.
*/
void cbRobot::updateState()
{
    State prevState = _state;

    switch(_state) {
        case RUNNING:
            if(removed) _state = REMOVED;

            else if (simulator->state() == cbSimulator::STOPPED) {
                _unstoppedState=_state;
                _state=STOPPED;
            }

            else if(visitingLedOn()) {
                     if(targetAtPos()==0) {
                        if(simulator->allRobotsVisitedOrVisitingTarget(0)
                           && simulator->allRobotsOnTarget(0)) {
			    setReturningLed(true);
		            _state = RETURNING;
                        }
                        else {
		            _state = WAITOTHERS;
                        }
		     }
                     else _state = FINISHED;
            }
            else if (endLed) {
	        _state = FINISHED;
	    }

            break;
        case WAITOTHERS:
            if(removed) _state = REMOVED;

            else if (simulator->state() == cbSimulator::STOPPED) {
                _unstoppedState=_state;
                _state=STOPPED;
            }

            else if(simulator->allRobotsVisitedOrVisitingTarget(0)
                    && simulator->allRobotsOnTarget(0)) {
			    setReturningLed(true);
		            _state = RETURNING;
            }
            else if (endLed) {
	        _state = FINISHED;
	    }

            break;
	case RETURNING:
           if(removed) _state = REMOVED;

           else if (simulator->state() == cbSimulator::STOPPED) {
                _unstoppedState=_state;
                _state=STOPPED;
           }

           else if(endLed) _state = FINISHED;

	   break;
        case STOPPED:
            if(removed) _state = REMOVED;
            else if(simulator->state() != cbSimulator::STOPPED)
                      _state=_unstoppedState;
            break;
        case FINISHED:
            if(removed) _state = REMOVED;
	default:
	    break;
    }

    if (prevState != _state)
    {
        emit robStateChanged(_state);
        emit robStateChanged(QString(curStateAsString()));
    }
}

/*!
	Determines the score component determined by distance to initial position.
*/
unsigned int cbRobot::distFromInitScore(void)
{
     // add current position to grAux
     simulator->grAux->addFinalPoint(id,curPos.Coord());
     // determine distance score, id determines initial position
     //return (unsigned int)(100*simulator->grAux->dist(id)/distAtArrival);
     return (unsigned int)(arrivalTimePenalty*simulator->grAux->dist(id)/distAtArrival);
}

unsigned int cbRobot::distFromInitScoreCompetitive(void)
{
     // add current position to grAux
     simulator->grAux->addFinalPoint(id,curPos.Coord());
     // determine distance score, id determines initial position
     return (unsigned int)(100*simulator->grAux->dist(id)/distAtArrival);
     //return (unsigned int)(arrivalTimePenalty*simulator->grAux->dist(id)/distAtArrival);
}

/*!
	Determines the score component determined by the time taken to return
*/

//#define RETURNTIMEPENALTY 25

unsigned int cbRobot::returnTimeScore(void)
{
	if(returningTime<distHomeToTarget/0.15)
		return 0;
	
    return (int)(returningTime-((int)(distHomeToTarget/0.15)))/returnTimePenalty;
}

unsigned int cbRobot::returnTimeScoreCompetitive(void)
{
	if(returningTime<distAtArrival/0.15)
		return 0;
	
    return (int)(returningTime-((int)(distAtArrival/0.15)))/returnTimePenalty;
}

//#define ARRIVALTIMEPENALTY 100

unsigned int cbRobot::arrivalTimeScore(void)
{
	return 0;   //HACK - CiberRato 2008 will not consider this score factor

	if(arrivalTime<distGridToBeacon/0.15)
		return 0;
	
    return (int)(arrivalTime-((int)(distGridToBeacon/0.15)))/arrivalTimePenalty;
}

/*!
	Update robot score. Called before updateState!
*/

//#define COLLISION_PENALTY   2
//#define NOTFINISH_PENALTY  15
//#define BASESCORE         0

/*!
	Update robot state.
*/
void cbRobot::updateStateCompetitive()
{
    switch(_state) {
        case RUNNING:
            if(removed) _state = REMOVED;

            else if (simulator->state() == cbSimulator::STOPPED) {
                _unstoppedState=_state;
                _state=STOPPED;
            }

            else if (endLed) {
	        _state = FINISHED;
	    }

            else if (returningLed) {
                    //fprintf(stderr,"RETURNINGLEDON targetAtPos %d visitall %d\n",targetAtPos(), visitedAllTargets());
                    if(targetAtPos()!=-1 && visitedAllTargets()) {
		        _state = RETURNING;
		    }
                    else _state = FINISHED;
	    }

            break;
        case RETURNING:
            if(removed) _state = REMOVED;

            else if (simulator->state() == cbSimulator::STOPPED) {
                _unstoppedState=_state;
                _state=STOPPED;
            }

            else if(endLed) _state = FINISHED;

            break;
        case STOPPED:
            if(removed) _state = REMOVED;
            else if(simulator->state() != cbSimulator::STOPPED)
                      _state=_unstoppedState;
            break;
        case FINISHED:
            if(removed) _state = REMOVED;
	default:
	    break;
    }
}



#define COLLISION_PENALTY   5
#define NOTFINISH_PENALTY  15
#define BASESCORE         100

void cbRobot::updateScoreCompetitive()
{
    if (isRemoved() || hasFinished()) return;
    
    if (hasCollide() && !collisionPrevCycle)
    {
        //DEBUG
	//simulator->grAux->addFinalPoint(id,curPos.Coord());
        //double distCol=simulator->grAux->dist(id);
	//cerr << simulator->curTime() << ": R" << id << " distCol=" << distCol <<"\n";
        scorePenalties += (collisionWallPenalty * hasCollideWall()) + (collisionRobotPenalty * hasCollideRobot());
	collisionCount++;

        emit robCollisionsChanged((int) collisionCount);
    }
    collisionPrevCycle=hasCollide();

    switch(_state) {
	    case RUNNING:
		 {
		    //score = BASESCORE + scorePenalties;  // BASESCORE must be equal to 
		                                         // distFromInitScore+returnTimeScore if robot finishes just after signaling return
		    score = scorePenalties;  // BASESCORE must be equal to 

		    if(endLedOn() && targetAtPos()>=0 && visitedAllTargets()) { // robot finishing at Beacon
                        simulator->grAux->addFinalPoint(id,curPos.Coord());
                        distAtArrival=simulator->grAux->dist(id);
			//cerr << simulator->curTime()<< ": R" << id << " distAtArrival=" << distAtArrival << "\n";
			arrivalTime=simulator->curTime();
			startReturningTime = simulator->curTime();
			returningTime=0;
                        score=scorePenalties + distFromInitScoreCompetitive()+returnTimeScoreCompetitive();
		    }
		    else if(returningLed && targetAtPos()>=0 && visitedAllTargets()) { // robot starting to return
                        simulator->grAux->addFinalPoint(id,curPos.Coord());
                        distAtArrival=simulator->grAux->dist(id);
			//cerr << simulator->curTime()<< ": R" << id << " distAtArrival=" << distAtArrival << "\n";
			startReturningTime = simulator->curTime();
			returningTime=0;

			scorePenalties -= 100;
                        score=scorePenalties + distFromInitScoreCompetitive()+returnTimeScoreCompetitive();
		    }
		    else if(visitingLedOn()) {
			    int t=targetAtPos();
			    if(t>=0) {
				    if(!targetVisited[t]) {
				        targetVisited[t] = true;
				        scorePenalties -= 100;
			            }
			    }
			    else scorePenalties+=5;
		            score = BASESCORE + scorePenalties;
		    }
		    if(nVisitedTargets()==0)
		        arrivalTime = simulator->curTime(); 
		    break;
		 }
            case RETURNING:
		 {
		    if(simulator->curTime()==simulator->simTime() 
				    && !endLed) // check if robot has just turned endLed on
			    scorePenalties+=NOTFINISH_PENALTY;

		    returningTime=simulator->curTime() - startReturningTime;
		    score = scorePenalties + distFromInitScoreCompetitive() + returnTimeScoreCompetitive();
                        //fprintf(stderr,"RETURN pen %d dist %d time %d\n", scorePenalties, distFromInitScoreCompetitive(), returnTimeScoreCompetitive());

		    if(returningLed && receivedReturningLed() && targetAtPos()>=0 && visitedAllTargets()) { // robot restarting to return
                        simulator->grAux->addFinalPoint(id,curPos.Coord());
                        distAtArrival=simulator->grAux->dist(id);
			//cerr << simulator->curTime()<< ": R" << id << " distAtArrival=" << distAtArrival << "\n";
			startReturningTime = simulator->curTime();
			returningTime=0;
                        score=scorePenalties + distFromInitScoreCompetitive() + returnTimeScoreCompetitive();
                        //fprintf(stderr,"RESTART pen %d dist %d time %d\n", scorePenalties, distFromInitScoreCompetitive(), returnTimeScoreCompetitive());
		    }
		    else if(visitingLedOn()) {
			    int t=targetAtPos();
			    if(t>=0) {
				    if(!targetVisited[t]) {
				        targetVisited[t] = true;
				        scorePenalties -= 100;
			            }
			    }
			    else scorePenalties+=5;
		            score = scorePenalties + distFromInitScoreCompetitive() + returnTimeScoreCompetitive();
                            //fprintf(stderr,"VISITON pen %d dist %d time %d\n", scorePenalties, distFromInitScoreCompetitive(), returnTimeScoreCompetitive());
		    }
		    break;
		 }
	   default:
		    break;
    }
    emit robArrivalTimeChanged((int) arrivalTime);
    emit robReturnTimeChanged((int) returningTime);
    emit robScoreChanged((int) score);
}



void cbRobot::updateScore()
{
    if (isRemoved() || hasFinished()) return;
    
    if (hasCollide() && !collisionPrevCycle)
    {
        //DEBUG
        //simulator->grAux->addFinalPoint(id,curPos.Coord());
        //double distCol=simulator->grAux->dist(id);
        //cerr << simulator->curTime() << ": R" << id << " distCol=" << distCol <<"\n";
        //scorePenalties += COLLISION_PENALTY;
        scorePenalties += (collisionWallPenalty * hasCollideWall()) + (collisionRobotPenalty * hasCollideRobot());
        collisionCount++;

        emit robCollisionsChanged((int) collisionCount);
    }
    //collisionPrevCycle=collision;
    collisionPrevCycle = hasCollide();

    switch(_state) {
	    case RUNNING:
        case WAITOTHERS:
        {
            if(distGridToBeacon==0.0) {
                simulator->grAux->addFinalPoint(id,getSimulator()->Lab()->Beacon(0)->Center()); // VALID ONLY FOR ONE BEACON MAZES
                distGridToBeacon = simulator->grAux->dist(id);
            }

            if(distHomeToTarget==0.0) {
                simulator->grAux->addFinalPoint(1,getSimulator()->Lab()->Beacon(0)->Center()); // VALID ONLY FOR ONE BEACON MAZES
                distHomeToTarget = simulator->grAux->dist(1); // ROBOT 1 will always be at center of Home area
		    }

            score = scorePenalties + arrivalTimeScore();

		    if(visitingLedOn() && targetAtPos()==0 && _state == RUNNING) { // robot visiting Target Area

                targetVisited[targetAtPos()] = true;
                if(simulator->curTime() < simulator->keyTime()
                        || simulator->keyTime()>=simulator->simTime())
                    //scorePenalties -= 100;
                    scorePenalties -= targetReward;
                else
                    //scorePenalties -= 50 + 50 * (simulator->simTime() - simulator->curTime())/(simulator->simTime()-simulator->keyTime());
                    scorePenalties -= targetReward/2 + targetReward/2 * (simulator->simTime() - simulator->curTime())/(simulator->simTime()-simulator->keyTime());

                simulator->grAux->addFinalPoint(id,curPos.Coord());
                //cerr << simulator->curTime()<< ": R" << id << " distAtArrival=" << distAtArrival << "\n";
                arrivalTime=simulator->curTime();

		        score = scorePenalties + arrivalTimeScore();  
		    }
		    if(nVisitedTargets()==0 && _state == RUNNING)
		        arrivalTime = simulator->curTime(); 
		    if(nVisitedTargets()==1)
		        startReturningTime = simulator->curTime(); 
		    break;

		 }

	   case RETURNING: {
	            returningTime = simulator->curTime() - startReturningTime; 
		    if(endLedOn() && targetAtPos()==1) { // robot finishing at Home Area

		        targetVisited[targetAtPos()] = true;
                //scorePenalties -= 100;
                scorePenalties -= homeReward;

		    }
		    score = scorePenalties + returnTimeScore();  
		
           }
	   default:
		    break;
    }

    emit robArrivalTimeChanged((int) arrivalTime);
    emit robReturnTimeChanged((int) returningTime);
    emit robScoreChanged((int) score);
}

/*!
	Update all sensors in robot.
*/
void cbRobot::updateSensors()
{
	unsigned int s;
	for(s=0; s < sensors.size(); s++)
		sensors[s]->update();
}

/*!
	Send sensor measures and led states to robots.
*/
void cbRobot::sendSensors()
{
	char xml[16*1024];
	unsigned int n;
	n = sprintf(xml, "<Measures Time=\"%u\">\n", simulator->curTime());
	/* add sensor information */
	n += sprintf(xml+n, "\t<Sensors");

	if(!collisionSensor->requestable || collisionSensor->requested)
	     n += sprintf(xml+n, " Collision=\"%s\"", collisionSensor->Value()?"Yes":"No");

	if(!compassSensor->requestable || compassSensor->requested)
	     n += sprintf(xml+n, " Compass=\"%g\"", compassSensor->Degrees());

	if(!groundSensor->requestable || groundSensor->requested)
	     n += sprintf(xml+n, " Ground=\"%d\"", groundSensor->Value());

	n += sprintf(xml+n, ">\n"); //end of attributes

	//IRSensors
	for(int i=0; i < NUM_IR_SENSORS; i++) {
		if(!irSensors[i]->requestable ||irSensors[i]->requested) {
		    n += sprintf(xml+n,"\t\t<IRSensor Id=\"%d\" Value=\"%g\"/>\n",
				i, irSensors[i]->Value());
		}
	}

	//beaconSensors
	for(unsigned int b=0; b<beaconSensors.size();b++)
	{
	    if(!beaconSensors[b]->requestable || beaconSensors[b]->requested) {
	        if(beaconSensors[b]->Ready()){
		    n += sprintf(xml+n, "\t\t<BeaconSensor Id=\"%d\" Value=", b);
	            if(beaconSensors[b]->BeaconVisible())
	                n += sprintf(xml+n, "\"%g\"", beaconSensors[b]->Degrees());
	            else
	                n += sprintf(xml+n, "\"NotVisible\"");
		    n += sprintf(xml+n, "/>\n");
	        }
	    }
    }

    //GPS
    if(GPSOn) {
	   if(!GPSSensor->requestable || GPSSensor->requested) {
	       n += sprintf(xml+n, "\t\t<GPS X=\"%g\" Y=\"%g\" ", GPSSensor->X(), GPSSensor->Y());
	       if(GPSDirOn)
	           n += sprintf(xml+n, " Dir=\"%g\" ", GPSSensor->Degrees());
	       n += sprintf(xml+n, "/>\n"); 
       }
    }

    //Message
    unsigned int nRobots=simulator->Robots().size();
    for(unsigned int r=0; r < nRobots; r++) {
        if(simulator->Robots()[r]
            && simulator->Robots()[r]->Center().distance(curPos.Coord()) < 8.0  // MESSAGE_DIST_LIMIT
            && simulator->Robots()[r]->getSayMessage()!="")
            n += sprintf(xml+n, "\t\t<Message From=\"%d\"><![CDATA[%s]]></Message>\n" ,
                         r+1, simulator->Robots()[r]->getSayMessage().toLatin1().constData());
    }

    if(scoreSensorOn) {
	   char visitedMask[256];
	   int t;
	   //determine visitedMask
	   for(t = 0; t < (int) simulator->Lab()->nTargets(); t++) {
	        visitedMask[t]= '0' + (targetVisited[t] ? 1: 0);
	   }
     	   visitedMask[t]='\0';
	   n += sprintf(xml+n, "\t\t<Score Score=\"%d\" ArrivalTime=\"%d\" ReturningTime=\"%d\" "
			                  "Collisions=\"%d\" Collision=\"%s\" VisitedMask=\"%s\" />\n", 
                    score, arrivalTime,returningTime,collisionCount, (hasCollide()?"True":"False"), visitedMask);
    }

	n += sprintf(xml+n, "\t</Sensors>\n");
	/* add end led information */
	n += sprintf(xml+n, "\t<Leds EndLed=\"%s\" ReturningLed=\"%s\" VisitingLed=\"%s\"/>\n", 
			    endLed?"On":"Off", returningLed?"On":"Off", visitingLed?"On":"Off");
	/* add buttons information */
	n += sprintf(xml+n, "\t<Buttons Start=\"%s\" Stop=\"%s\"/>\n",
			simulator->getNextState()==cbSimulator::RUNNING?"On":"Off",
                        simulator->getNextState()==cbSimulator::STOPPED?"On":"Off");
	n += sprintf(xml+n, "</Measures>\n");

	/* send XML message to client */
	socket->send(xml, n);
	
#ifdef DEBUG_ROBOT
	cerr << "Measures sent to robot " << id << "\n" << xml;
#endif

    if (showMeasures)
        simulator->GUI()->writeOnBoard("Measures sent to " + QString(name) + "(robot " + QString::number(id) + ")" + ":\n" + xml, (int) id, 0);

}


/*!
	Fill in given xml buffer with robot state, that is, name, id, 
	score, number of collisions, the collision state, removed states, and current position.
	Return the length of the xml message.
*/

#define LOGWITHMEASURES

unsigned int cbRobot::toXml(char *xml, unsigned int len, bool withActions) // len = buffer size not used
{
	char visitedMask[256];
    int t;
    unsigned int n;
    n = sprintf(xml, "\t<Robot Name=\"%s\" Id=\"%u\" State=\"%s\">\n", Name(), Id(), StrState[_state]);
    n += sprintf(xml+n, "\t\t<Pos X=\"%f\" Y=\"%f\" Dir=\"%f\"/>\n", X(), Y(), Degrees());
	
	// Determine visitedMask
	for(t = 0; t < (int) simulator->Lab()->nTargets(); t++) {
	    visitedMask[t]= '0' + (targetVisited[t] ? 1: 0);
	}
	visitedMask[t]='\0';

	n += sprintf(xml+n, "\t\t<Scores Score=\"%u\" ArrivalTime=\"%u\" ReturningTime=\"%u\" Collisions=\"%u\" "
						"Collision=\"%s\" VisitedMask=\"%s\"/>\n", score, arrivalTime, returningTime, 
						collisionCount, hasCollide() ? "True" : "False", visitedMask);

    if(withActions && receivedAction())
    {
    	n += sprintf(xml+n, "\t\t<Action");
	    if(receivedLeftMotor())
	    	n += sprintf(xml+n, " LeftMotor=\"%f\"", LeftMotor().inPower());
	    if(receivedRightMotor())
	        n += sprintf(xml+n, " RightMotor=\"%f\"", RightMotor().inPower());
	    if(receivedEndLed())
	    	n += sprintf(xml+n, " EndLed=\"%s\"", endLedOn() ? "On":"Off");
	    if(receivedReturningLed())
	    	n += sprintf(xml+n, " ReturningLed=\"%s\"", returningLedOn() ? "On":"Off");
	    if(receivedVisitingLed())
	    	n += sprintf(xml+n, " VisitingLed=\"%s\"", visitingLedOn() ? "On":"Off");
	    n += sprintf(xml+n, " />\n");
	}

#ifdef LOGWITHMEASURES
	n += sprintf(xml+n, "\t\t<Measures Time=\"%u\">\n", simulator->curTime());
	/* add sensor information */
	n += sprintf(xml+n, "\t\t\t<Sensors");
	n += sprintf(xml+n, " Compass=\"%g\"", compassSensor->Degrees());

	n += sprintf(xml+n, " Collision=\"%s\"", collisionSensor->Value()?"Yes":"No");
	n += sprintf(xml+n, " Ground=\"%d\">\n", groundSensor->Value());

	for(int i=0; i < NUM_IR_SENSORS; i++)
		n += sprintf(xml+n,"\t\t\t\t<IRSensor Id=\"%d\" Value=\"%g\"/>\n",
				i, irSensors[i]->Value());

	for(unsigned int b=0; b < beaconSensors.size(); b++) {
        if(beaconSensors[b]->Ready()){
            n += sprintf(xml+n, "\t\t\t\t<BeaconSensor Id=\"%d\" Value=", b);
	        if(beaconSensors[b]->BeaconVisible())
	            n += sprintf(xml+n, "\"%g\"", beaconSensors[b]->Degrees());
	        else
                n += sprintf(xml+n, "\"NotVisible\"");
            n += sprintf(xml+n, "/>\n");
	    }
	}

    if(GPSOn) {
	   n += sprintf(xml+n, "\t\t\t\t<GPS X=\"%g\" Y=\"%g\" ", 
                    GPSSensor->X(), GPSSensor->Y());
       if(GPSDirOn) n += sprintf(xml+n, " Dir=\"%g\" ", GPSSensor->Degrees());
       n += sprintf(xml+n, "/>\n");
    }

	n += sprintf(xml+n, "\t\t\t</Sensors>\n");
	/* add end led information */
	n += sprintf(xml+n, "\t\t\t<Leds EndLed=\"%s\" ReturningLed=\"%s\" VisitingLed=\"%s\"/>\n", 
			    endLed?"On":"Off", returningLed?"On":"Off", visitingLed?"On":"Off");
	/* add buttons information */
	n += sprintf(xml+n, "\t\t\t<Buttons Start=\"%s\" Stop=\"%s\"/>\n",
			simulator->getNextState()==cbSimulator::RUNNING?"On":"Off",
                        simulator->getNextState()==cbSimulator::STOPPED?"On":"Off");
	n += sprintf(xml+n, "\t\t</Measures>\n");
#endif

    n += sprintf(xml+n, "\t</Robot>\n");

    if(n > len-1) {
        fprintf(stderr,"cbRobot::toXml message is too long\n");
        abort();
    }

	//if(returningTime > 0) cerr << "returnTime=" << returningTime << " startRet=" << startReturningTime << "\n";
	//cerr << xml;

	return n;
}


void cbRobot::showAllAttributes()
{
	char xml[16*1024];
	/* add global robot information */
	unsigned int n = toXml(xml, 1024);
	n = n - 9;	// go back </Robot> tag
	double dir = nextPos.directionInDegrees();
	n += sprintf(xml+n, "\t<NextPosition X=\"%g\" Y=\"%g\" Dir=\"%g\"/>\n", 
			nextPos.X(), nextPos.Y(), dir);
	n += sprintf(xml+n, "\t<LeftMotor InPower=\"%g\" OutPower=\"%g\"/>\n", 
			leftMotor.inPower(), leftMotor.lastOutPower());
	n += sprintf(xml+n, "\t<RightMotor InPower=\"%g\" OutPower=\"%g\"/>\n", 
			rightMotor.inPower(), rightMotor.lastOutPower());
	n += sprintf(xml+n, "\t<EndLed State=\"%s\"/>\n", endLed?"On":"Off");
	n += sprintf(xml+n, "\t<Measures Time=\"%u\">\n", simulator->curTime());
	/* add sensor information */
	n += sprintf(xml+n, "\t\t<Sensors");
	n += sprintf(xml+n, " Compass=\"%g\"", compassSensor->Degrees());
	n += sprintf(xml+n, " Collision=\"%s\"", collisionSensor->Value()?"Yes":"No");
	n += sprintf(xml+n, " Ground=\"%d\">\n", groundSensor->Value());
	for(int i=0; i < NUM_IR_SENSORS; i++)
		n += sprintf(xml+n,"\t\t<IRSensor Id=\"%d\" Value=\"%g\"/>",
				i, irSensors[i]->Value());
	for(unsigned int b=0; b < beaconSensors.size(); b++) {
	    if(beaconSensors[b]->Ready()){
		n += sprintf(xml+n, "\t\t<BeaconSensor Id=\"%d\" Value=", b);
	        if(beaconSensors[b]->BeaconVisible())
	            n += sprintf(xml+n, "\"%g\"", beaconSensors[b]->Degrees());
	        else
	            n += sprintf(xml+n, "\"NotVisible\"");
		n += sprintf(xml+n, "/>\n");
	    }
	}
	n += sprintf(xml+n, "\t\t</Sensors>\n");
	/* add end led information */
	n += sprintf(xml+n, "\t\t<Leds EndLed=\"%s\"/>\n", endLed?"On":"Off");
	/* add buttons information */
	n += sprintf(xml+n, "\t\t<Buttons Start=\"%s\" Stop=\"%s\"/>\n",
            simulator->getNextState()==cbSimulator::RUNNING?"On":"Off", 
            simulator->getNextState()==cbSimulator::STOPPED?"On":"Off");
	n += sprintf(xml+n, "\t</Measures>\n");
	n += sprintf(xml+n, "</Robot>\n");

	cout << xml;
}

// cbRobotBin

#include "netif.h"


bool cbRobotBin::Reply(QHostAddress &a, unsigned short &p, cbParameters *param)
{
	//cout.form("Sending reply for client to %s:%hd\n", a.toString().latin1(), p);
	/* set peer address and peer port */
    address = a;
	port = p;

	/* constructing reply message */
    CommMessage commMsg;

    commMsg.comm=htons(OK_COMM);

    commMsg.u.params.cycle_time= htons(param->cycleTime);
    //commMsg.u.params.sim_time_final  =htons(sim_time);
    //commMsg.u.params.noise_obstacles =htons( (unsigned short) (noise_obstacles*10.0+0.5) );
    //commMsg.u.params.noise_beacon    =htons( (unsigned short) (noise_beacon+0.5));
    //commMsg.u.params.noise_compass   =htons( (unsigned short) (noise_compass+0.5));
    //commMsg.u.params.noise_motors    =htons( (unsigned short) (noise_motors*10.0+0.5));
   

    /* send reply to client */
    if (socket->write((char *)&commMsg, sizeof(CommMessage)) != sizeof(CommMessage))
	{
        cerr << "Fail replying to client\n";
        simulator->GUI()->appendMessage( "Fail replying to client", true);
		return false;
	}

    //cout << "Reply sent\n" << reply;
	return true;
}


bool cbRobotBin::readAction(cbRobotAction *action)
{
	QByteArray datagram, readArr;
    while (strcmp((readArr = socket->read(1)).data(), "\x04") != 0) {
        if (readArr.isEmpty()) {
            cerr << "Delimeter not found in the message, check the message sent.\n";
            return false;
        }
        datagram += readArr;
    }
#ifdef DEBUG_ROBOT
	cerr << "cbRobot: " << datagram.data() << "\n";
#endif

    if (showActions)
        simulator->GUI()->writeOnBoard(QString(name) + " : " + datagram, (int) id, 1);

	/* parse xml message */
	QXmlSimpleReader parser;
    QXmlInputSource source;
    parser.setContentHandler(&handler);
    source.setData(datagram);
	if (!parser.parse(source))
	{
        cerr << "cbRobot::Fail parsing xml action message: \"" << datagram.constData() << "\"\n";
        simulator->GUI()->appendMessage( "cbRobot: Fail parsing xml action message:" , true);
        simulator->GUI()->appendMessage( QString(" \"")+datagram.constData()+"\"" , true);

		return false;
	}
	
	*action = handler.parsedAction();

#ifdef DEBUG_ROBOT
    cerr << "actions received from robot\n";
#endif

    return true;
}

void cbRobotBin::sendSensors()
{

   SenseMessage msg;

   msg.time=htons((unsigned short)simulator->curTime());

   msg.center   =htons((unsigned short) (irSensors[1]->Value()*10.0 + 0.5) );
   msg.left     =htons((unsigned short) (irSensors[0]->Value()*10.0 + 0.5) );
   msg.right    =htons((unsigned short) (irSensors[2]->Value()*10.0 + 0.5) );

   msg.light    =htons((unsigned short) (beaconSensors[0]->Degrees()+360.0 + 0.5) );
   msg.compass  =htons((unsigned short) (compassSensor->Degrees()+360.0 + 0.5) );
   msg.ground   =htons((unsigned short) groundSensor->Value() );
   msg.collision=htons((unsigned short) collisionSensor->Value() );
   msg.start    = htons((unsigned short) (simulator->getNextState()==cbSimulator::RUNNING) );
   msg.stop     = htons((unsigned short) (simulator->getNextState()==cbSimulator::STOPPED) );
   msg.endLed   = htons((unsigned short) endLed);


	/* send XML message to client */
	socket->send((char *)&msg, sizeof(msg));
#ifdef DEBUG_ROBOT
	cerr << "Measures sent to robot (bin protocol)\n";
#endif
}

/*!
	Send the Refused reply message to client.
*/
bool cbRobotBin::Refuse(QHostAddress &a, unsigned short &p)
{
	//cout.form("Sending refuse for client to %s:%hd\n", a.toString().latin1(), p);
	/* set peer address and peer port */
	address = a;
    port = p;

    CommMessage commMsg;

    commMsg.comm=htons(OK_COMM+1);

    socket->send((char *)&commMsg,sizeof(commMsg));

	return true;
}
