# This is a sample of a preparation script to install all the dependencies and compile
# your code.
echo "Unzip sample_code.zip.."
unzip sample_code.zip
cd sample_code;
echo "Compiling source code.."
javac jClient.java ciberIF/ciberIF.java ciberIF/beaconMeasure.java ciberIF/gpsMeasure.java
echo "Done."