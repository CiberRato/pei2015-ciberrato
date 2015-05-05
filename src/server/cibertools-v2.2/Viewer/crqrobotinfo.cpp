#include "crqrobotinfo.h"
#include "ui_crqrobotinfo.h"

#include <QtCore>
#include <QtGui>

using namespace std;

CRQRobotInfo::CRQRobotInfo(CRRobot *rob, QString skinName, QWidget *parent) :
    QWidget(parent),
    ui(new Ui::CRQRobotInfo)
{
    ui->setupUi(this);

    skin(skinName); /* Change skin */
    robot = rob;

    ui->lcdNumber_ID->display(rob->id());

    QPixmap *pixx = new QPixmap(robFiles[rob->id()]);
    QMatrix mat;
    QPixmap tmp = pixx->transformed(mat.rotate(-90));
    ui->label_Icon->setPixmap(tmp.scaled(ui->label_Icon->size()));

    // NOME
    ui->label_Name->setText( robot->name() );

    // RETURN TIME
    connect(this, SIGNAL(time(int)), ui->lcdNumber_Time, SLOT(display(int)));

    // SCORE
    connect(this, SIGNAL(score(int)), ui->lcdNumber_Score, SLOT(display(int)));

    // COLISOES
    connect(this, SIGNAL(collisions(int)), ui->lcdNumber_Collisions, SLOT(display(int)));

    // ESTADO
    previousState = CRRobot::STOPPED;
    ui->label_State->setPixmap( stopPix );
    connect( this, SIGNAL( state(QPixmap) ), ui->label_State,
             SLOT(setPixmap(QPixmap)));

    ui->label_State->setToolTip(rob->stateAsString());

}

CRQRobotInfo::~CRQRobotInfo()
{
    delete ui;
}

void CRQRobotInfo::skin(QString skinName)
{
    char rob1File[4096];
    char rob2File[4096];
    char rob3File[4096];
    char rob4File[4096];
    char rob5File[4096];
    char rob6File[4096];
    char rob7File[4096];
    char rob8File[4096];
    char rob9File[4096];
    char rob10File[4096];
    char rob11File[4096];
    char rob12File[4096];
    char rob13File[4096];
    char rob14File[4096];
    char rob15File[4096];
    char rob16File[4096];
    char rob17File[4096];
    char rob18File[4096];
    char rob19File[4096];
    char rob20File[4096];
    char backFile[4096];
    char runFile[4096];
    char waitFile[4096];
    char stopFile[4096];
    char returnFile[4096];
    char removeFile[4096];
    char finishFile[4096];


    strcpy(backFile, "skins/");
    strcat(backFile, skinName.toAscii());
    strcat(backFile, "/robbg.png");

    strcpy(rob1File, "skins/");
    strcat(rob1File, skinName.toAscii());
    strcat(rob1File, "/rob1/rob.png");

    strcpy(rob2File, "skins/");
    strcat(rob2File, skinName.toAscii());
    strcat(rob2File, "/rob2/rob.png");

    strcpy(rob3File, "skins/");
    strcat(rob3File, skinName.toAscii());
    strcat(rob3File, "/rob3/rob.png");

    strcpy(rob4File, "skins/");
    strcat(rob4File, skinName.toAscii());
    strcat(rob4File, "/rob4/rob.png");

    strcpy(rob5File, "skins/");
    strcat(rob5File, skinName.toAscii());
    strcat(rob5File, "/rob5/rob.png");

    strcpy(rob6File, "skins/");
    strcat(rob6File, skinName.toAscii());
    strcat(rob6File, "/rob5/rob.png");

    strcpy(rob7File, "skins/");
    strcat(rob7File, skinName.toAscii());
    strcat(rob7File, "/rob5/rob.png");

    strcpy(rob8File, "skins/");
    strcat(rob8File, skinName.toAscii());
    strcat(rob8File, "/rob5/rob.png");

    strcpy(rob9File, "skins/");
    strcat(rob9File, skinName.toAscii());
    strcat(rob9File, "/rob5/rob.png");

    strcpy(rob10File, "skins/");
    strcat(rob10File, skinName.toAscii());
    strcat(rob10File, "/rob5/rob.png");

    strcpy(rob11File, "skins/");
    strcat(rob11File, skinName.toAscii());
    strcat(rob11File, "/rob5/rob.png");

    strcpy(rob12File, "skins/");
    strcat(rob12File, skinName.toAscii());
    strcat(rob12File, "/rob5/rob.png");

    strcpy(rob13File, "skins/");
    strcat(rob13File, skinName.toAscii());
    strcat(rob13File, "/rob5/rob.png");

    strcpy(rob14File, "skins/");
    strcat(rob14File, skinName.toAscii());
    strcat(rob14File, "/rob5/rob.png");

    strcpy(rob15File, "skins/");
    strcat(rob15File, skinName.toAscii());
    strcat(rob15File, "/rob5/rob.png");

    strcpy(rob16File, "skins/");
    strcat(rob16File, skinName.toAscii());
    strcat(rob16File, "/rob5/rob.png");

    strcpy(rob17File, "skins/");
    strcat(rob17File, skinName.toAscii());
    strcat(rob17File, "/rob5/rob.png");

    strcpy(rob18File, "skins/");
    strcat(rob18File, skinName.toAscii());
    strcat(rob18File, "/rob5/rob.png");

    strcpy(rob19File, "skins/");
    strcat(rob19File, skinName.toAscii());
    strcat(rob19File, "/rob5/rob.png");

    strcpy(rob20File, "skins/");
    strcat(rob20File, skinName.toAscii());
    strcat(rob20File, "/rob5/rob.png");

    robFiles << backFile << rob1File << rob2File << rob3File << rob4File << rob5File << rob6File << rob7File << rob8File << rob9File << rob10File << rob11File << rob12File << rob13File << rob14File << rob15File << rob16File << rob17File << rob18File << rob19File << rob20File;

    strcpy(runFile, "skins/");
    strcat(runFile, skinName.toAscii());
    strcat(runFile, "/states/running.png");

    strcpy(waitFile, "skins/");
    strcat(waitFile, skinName.toAscii());
    strcat(waitFile, "/states/waiting.png");

    strcpy(stopFile, "skins/");
    strcat(stopFile, skinName.toAscii());
    strcat(stopFile, "/states/stopped.png");

    strcpy(returnFile, "skins/");
    strcat(returnFile, skinName.toAscii());
    strcat(returnFile, "/states/returning.png");

    strcpy(removeFile, "skins/");
    strcat(removeFile, skinName.toAscii());
    strcat(removeFile, "/states/removed.png");

    strcpy(finishFile, "skins/");
    strcat(finishFile, skinName.toAscii());
    strcat(finishFile, "/states/finished.png");

    QSize scale = ui->label_State->size();
    stopPix = QPixmap(stopFile).scaled(scale);
    runPix = QPixmap(runFile).scaled(scale);
    waitPix = QPixmap(waitFile).scaled(scale);
    returnPix = QPixmap(returnFile).scaled(scale);
    removePix = QPixmap(removeFile).scaled(scale);
    finishPix = QPixmap(finishFile).scaled(scale);

}

void CRQRobotInfo::update( CRRobot * rob)
{
    robot = rob;
    emit score( (int) robot->score() );
    emit collisions( (int) robot->collisions() );
    emit returnTime( (int) robot->returnTime() );
//2005	if(robot->state() == CRRobot::RUNNING)
//2005		emit time( (int) robot->currentTime() );
    emit time( (int) robot->arrivalTime() );

    if( previousState != robot->state() )
    {
        previousState = robot->state();
        switch ( robot->state() )
        {
        case CRRobot::STOPPED:
            emit state(stopPix);
            break;
        case CRRobot::RUNNING:
            emit state(runPix);
            break;
        case CRRobot::WAITINGOTHERS:
            emit state(waitPix);
            break;
        case CRRobot::REMOVED:
            emit state(removePix);
            break;
        case CRRobot::FINISHED:
            emit state(finishPix);
            break;
        case CRRobot::RETURNING:
            emit state(returnPix);
            break;
        }
        ui->label_State->setToolTip(robot->stateAsString());
    }
}
