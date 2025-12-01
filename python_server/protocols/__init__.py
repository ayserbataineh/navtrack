"""GPS Device Protocols."""

# Base imports
from .base import *

# Protocol implementations
from .coban import CobanProtocol, CobanMessageHandler
from .teltonika import TeltonikaProtocol, TeltonikaMessageHandler
from .meitrack import MeitrackProtocol, MeitrackMessageHandler
from .concox import ConcoxProtocol, ConcoxMessageHandler
from .queclink import QueclinkProtocol, QueclinkMessageHandler
from .tkstar import TkStarProtocol, TkStarMessageHandler
from .globalsat import GlobalSatProtocol, GlobalSatMessageHandler
from .totem import TotemProtocol, TotemMessageHandler
from .suntech import SuntechProtocol, SuntechMessageHandler
from .megastek import MegastekProtocol, MegastekMessageHandler
from .fifotrack import FifotrackProtocol, FifotrackMessageHandler
from .meiligao import MeiligaoProtocol, MeiligaoMessageHandler
from .xexun import XexunProtocol, XexunMessageHandler
from .istartek import iStartekProtocol, iStartekMessageHandler
from .eelink import EelinkProtocol, EelinkMessageHandler
from .gosafe import GosafeProtocol, GosafeMessageHandler
from .vjoycar import VjoyCarProtocol, VjoyCarMessageHandler
from .xirgo import XirgoProtocol, XirgoMessageHandler
from .tzone import TzoneProtocol, TzoneMessageHandler
from .gt06 import GT06Protocol, GT06MessageHandler
from .gpsmarker import GPSMarkerProtocol, GPSMarkerMessageHandler

# Protocol aliases and variations
from .sinotrack import SinoTrackProtocol, SinoTrackMessageHandler
from .lkgps import LKGPSProtocol, LKGPSMessageHandler
from .cantrack import CanTrackProtocol, CanTrackMessageHandler
from .carscop import CarscopProtocol, CarscopMessageHandler
from .reachfar import ReachFarProtocol, ReachFarMessageHandler
from .icargps import iCarGPSProtocol, iCarGPSMessageHandler
from .itracgps import iTracGPSProtocol, iTracGPSMessageHandler
from .xeelectech import XeElectechProtocol, XeElectechMessageHandler
from .smartrack import SmartrackProtocol, SmartrackMessageHandler
from .skypatrol import SkypatrolProtocol, SkypatrolMessageHandler

# Additional protocols
from .arknav import ArknavProtocol, ArknavMessageHandler
from .haicom import HaicomProtocol, HaicomMessageHandler
from .cartrackgps import CarTrackGPSProtocol, CarTrackGPSMessageHandler
from .kingsword import KingSwordProtocol, KingSwordMessageHandler
from .amwell import AmwellProtocol, AmwellMessageHandler
from .sanav import SanavProtocol, SanavMessageHandler
from .gotop import GotopProtocol, GotopMessageHandler
from .gopass import GoPassProtocol, GoPassMessageHandler
from .jointech import JointechProtocol, JointechMessageHandler
from .keson import KeSonProtocol, KeSonMessageHandler
from .bofan import BofanProtocol, BofanMessageHandler
from .blueidea import BlueIdeaProtocol, BlueIdeaMessageHandler
from .vsun import VSunProtocol, VSunMessageHandler
from .manpower import ManPowerProtocol, ManPowerMessageHandler
from .wondeproud import WondeProudProtocol, WondeProudMessageHandler
from .eview import EviewProtocol, EviewMessageHandler
from .freedom import FreedomProtocol, FreedomMessageHandler
from .topfly import TopflyProtocol, TopflyMessageHandler
from .laipac import LaipacProtocol, LaipacMessageHandler
from .pretrace import PretraceProtocol, PretraceMessageHandler
from .alematics import AlematicsProtocol, AlematicsMessageHandler
from .navtelecom import NavtelecomProtocol, NavtelecomMessageHandler
from .galileosky import GalileoskyProtocol, GalileoskyMessageHandler
from .ruptela import RuptelaProtocol, RuptelaMessageHandler
from .arusnavi import ArusnaviProtocol, ArusnaviMessageHandler
from .neomatica import NeomaticaProtocol, NeomaticaMessageHandler
from .satellite import SatelliteProtocol, SatelliteMessageHandler
from .autofon import AutofonProtocol, AutofonMessageHandler
from .atrack import ATrackProtocol, ATrackMessageHandler

# All protocols list for easy registration
ALL_PROTOCOLS = [
    (CobanProtocol, CobanMessageHandler),
    (TeltonikaProtocol, TeltonikaMessageHandler),
    (MeitrackProtocol, MeitrackMessageHandler),
    (ConcoxProtocol, ConcoxMessageHandler),
    (QueclinkProtocol, QueclinkMessageHandler),
    (TkStarProtocol, TkStarMessageHandler),
    (GlobalSatProtocol, GlobalSatMessageHandler),
    (TotemProtocol, TotemMessageHandler),
    (SuntechProtocol, SuntechMessageHandler),
    (MegastekProtocol, MegastekMessageHandler),
    (FifotrackProtocol, FifotrackMessageHandler),
    (MeiligaoProtocol, MeiligaoMessageHandler),
    (XexunProtocol, XexunMessageHandler),
    (iStartekProtocol, iStartekMessageHandler),
    (EelinkProtocol, EelinkMessageHandler),
    (GosafeProtocol, GosafeMessageHandler),
    (VjoyCarProtocol, VjoyCarMessageHandler),
    (XirgoProtocol, XirgoMessageHandler),
    (TzoneProtocol, TzoneMessageHandler),
    (GT06Protocol, GT06MessageHandler),
    (GPSMarkerProtocol, GPSMarkerMessageHandler),
    (SinoTrackProtocol, SinoTrackMessageHandler),
    (LKGPSProtocol, LKGPSMessageHandler),
    (CanTrackProtocol, CanTrackMessageHandler),
    (CarscopProtocol, CarscopMessageHandler),
    (ReachFarProtocol, ReachFarMessageHandler),
    (iCarGPSProtocol, iCarGPSMessageHandler),
    (iTracGPSProtocol, iTracGPSMessageHandler),
    (XeElectechProtocol, XeElectechMessageHandler),
    (SmartrackProtocol, SmartrackMessageHandler),
    (SkypatrolProtocol, SkypatrolMessageHandler),
    (ArknavProtocol, ArknavMessageHandler),
    (HaicomProtocol, HaicomMessageHandler),
    (CarTrackGPSProtocol, CarTrackGPSMessageHandler),
    (KingSwordProtocol, KingSwordMessageHandler),
    (AmwellProtocol, AmwellMessageHandler),
    (SanavProtocol, SanavMessageHandler),
    (GotopProtocol, GotopMessageHandler),
    (GoPassProtocol, GoPassMessageHandler),
    (JointechProtocol, JointechMessageHandler),
    (KeSonProtocol, KeSonMessageHandler),
    (BofanProtocol, BofanMessageHandler),
    (BlueIdeaProtocol, BlueIdeaMessageHandler),
    (VSunProtocol, VSunMessageHandler),
    (ManPowerProtocol, ManPowerMessageHandler),
    (WondeProudProtocol, WondeProudMessageHandler),
    (EviewProtocol, EviewMessageHandler),
    (FreedomProtocol, FreedomMessageHandler),
    (TopflyProtocol, TopflyMessageHandler),
    (LaipacProtocol, LaipacMessageHandler),
    (PretraceProtocol, PretraceMessageHandler),
    (AlematicsProtocol, AlematicsMessageHandler),
    (NavtelecomProtocol, NavtelecomMessageHandler),
    (GalileoskyProtocol, GalileoskyMessageHandler),
    (RuptelaProtocol, RuptelaMessageHandler),
    (ArusnaviProtocol, ArusnaviMessageHandler),
    (NeomaticaProtocol, NeomaticaMessageHandler),
    (SatelliteProtocol, SatelliteMessageHandler),
    (AutofonProtocol, AutofonMessageHandler),
    (ATrackProtocol, ATrackMessageHandler),
]
