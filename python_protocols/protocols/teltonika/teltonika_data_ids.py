class TeltonikaDataIds:
    EventId = 0

    # Permanent I/O elements
    DigitalInput1 = 1
    ICCID1 = 11
    ICCID2 = 14
    EcoScore = 15
    TotalOdometer = 16
    GsmSignal = 21
    GNSSSpeed = 24
    ExternalVoltage = 66
    BatteryVoltage = 67
    BatteryCurrent = 68
    GNSSStatus = 69
    BatteryLevel = 113
    GNSSPDOP = 181
    GNSSHDOP = 182
    TripOdometer = 199
    SleepMode = 200
    GsmCellId = 205
    GsmAreaCode = 206
    Ignition = 239
    Movement = 240
    ActiveGSMOperator = 241
    UMTSLTECellID = 636

    # Event I/O elements
    EventTrip = 250
    IgnitionOnCounter = 449

    # OBD elements
    ObdDtcCount = 30
    ObdEngineLoad = 31
    ObdCoolantTemperature = 32
    ObdShortTermFuelTrim = 33
    ObdFuelPressure = 34
    ObdIntakeManifoldAbsolutPressure = 35
    ObdEngineRpm = 36
    ObdSpeed = 37
    ObdTimingAdvance = 38
    ObdIntakeAirTemperature = 39
    ObdMAFAirFlowRate = 40
    ObdThrottlePosition = 41
    ObdRuntimeSinceEngineStart = 42
    ObdDistanceTraveledMILOn = 43
    ObdRelativeFuelRailPressure = 44
    ObdDirectFuelRailPressure = 45
    ObdCommandedEGR = 46
    ObdEGRError = 47
    ObdFuelLevel = 48
    ObdDistanceSinceCodesClear = 49
    ObdBarometicPressure = 50
    ObdControlModuleVoltage = 51
    ObdAbsoluteLoadValue = 52
    ObdAmbientAirTemperature = 53
    ObdTimeRunWithMILOn = 54
    ObdTimeSinceCodesCleared = 55
    ObdAbsoluteFuelRailPressure = 56
    ObdHybridBatteryPackLife = 57
    ObdEngineOilTemperature = 58
    ObdFuelInjectionTiming = 59
    ObdFuelRate = 60
    ObdVIN = 256
    ObdFaultCodes = 281
    ObdThrottlePositionGroup = 540
    ObdCommandedEquivalenceRatio = 541
    ObdIntakeMAP2Bytes = 542
    ObdHybridSystemVoltage = 543
    ObdHybridSystemCurrent = 544
    ObdFuelType = 759

    # OBD OEM elements
    ObdOemMileage = 389
    ObdOemFuelLevel = 390
    ObdOemDistanceUntilService = 402
    ObdOemBatteryChargeState = 410
    ObdOemBatteryLevel = 411
    ObdOemBatteryPowerConsumption = 412
    ObdOemRemainingDistance = 755
    ObdOemBatteryStateOfHealth = 1151
    ObdOemBatteryTemperature = 1152

    # CAN adapters
    CanDoorStatus = 90
    CanProgramNumber = 100
    CanFuelConsumedCounted = 107
    CanControlStateFlags = 123
    CanAgriculturalMachineryFlags = 124
    CanSecurityStateFlags = 132
    CanCNGStatus = 232
    CanSecurityStateFlagsP4 = 517
