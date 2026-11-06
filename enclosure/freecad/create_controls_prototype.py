"""FreeCAD MCP: new reversible control integration and independent fixtures.
Set MFQ_REPO_ROOT to the checkout. Does not save old CAD or modify electronics.
"""
from pathlib import Path
import json,hashlib,re,math
import Part,MeshPart,Mesh
from pivy import coin
root=Path(globals().get('MFQ_REPO_ROOT',r'C:\Users\djust\OneDrive\Documents\GitHub\my-first-qubit'))
cad=root/'enclosure/freecad'
outputs=[cad/('MyFirstQubit_'+s+'.FCStd') for s in ['iteration03_controls_prototype','encoder_knob_fixture','gate_button_fixture_PROVISIONAL','measure_button_fixture_PROVISIONAL']]
if any(p.exists() for p in outputs):raise RuntimeError('New revision already exists; refusing overwrite')
protected=[p for p in root.rglob('*') if p.is_file() and (p.suffix in ['.FCStd','.stl'] or 'firmware' in p.parts or p==root/'hardware/wiring.md' or p.name.endswith('validation.json'))]
hashes={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
source=cad/'MyFirstQubit_iteration03_LCD_PCB160.FCStd'
src=next((d for d in App.listDocuments().values() if d.FileName and Path(d.FileName)==source),None) or App.openDocument(str(source))
src.saveCopy(str(outputs[0]));assembly=App.openDocument(str(outputs[0]))
assembly.Label='Iteration 03 controls prototype - nominal Bourns / provisional tactile switches'
settings=App.ParamGet('User parameter:BaseApp/Preferences/Document');backups=settings.GetInt('CountBackupFiles',1);settings.SetInt('CountBackupFiles',0)
values={
 'PanelBottom':30.3,'PanelThickness':5,
 'EncoderSetback':7,'CarrierThickness':3,'CarrierWidth':36,'CarrierDepth':32,
 'EncoderBodyWidth':12.5,'EncoderBodyHeight':13.4,'EncoderBodyDepth':6.5,
 'BushingDiameter':7,'BushingLength':7,'ShaftDiameter':6,'ShaftFlatSpan':4.5,'ShaftLength':25,'FlatLength':12,
 'WasherOD':12,'WasherThickness':.5,'NutThickness':2,'NutAF':10,
 'BushingBoreTBD':7.4,'BodySideGapTBD':.5,'BodySkirtDepth':3.3,
 'EncoderPCBWidthTBD':20,'EncoderPCBDepthTBD':24,'PCBThicknessTBD':1.6,'EncoderBoardGapTBD':1,
 'TerminalPitch':2.5,'TerminalWidth':.8,'PinRearReachTBD':3.7,'EncoderWireDepthTBD':5,
 'KnobDiameter':40,'KnobHeight':14,'KnobRounding':3,'KnobFaceGap':1.3,
 'ShaftBoreDiameterTBD':6.4,'ShaftFlatGapTBD':.2,'ShaftTipGapTBD':.5,
 'KnobScrewHeight':8,'KnobScrewBoreTBD':3.4,'NutTrapX':8,'NutTrapDepthTBD':2.7,'NutTrapWidthTBD':5.7,'NutTrapHeightTBD':6.7,
 'EncoderMountX':14,'EncoderMountY':11,'MountBoreTBD':2.8,'MountPilotTBD':2,'EncoderMountScrewLengthTBD':8,
 'GateDiameter':28,'MeasureDiameter':36,'SecondaryDiameter':22,'CapAboveFace':4.5,'CapRounding':2,
 'GuideRadialGapTBD':.3,'CapFlangeExtra':4,'CapFlangeThickness':1.5,'TravelStopTBD':.6,
 'GuideWall':1.7,'StopShelfThickness':1.5,'GuideEarExtra':6,'GuideEarDiameter':7,
 'ButtonDeckWidthTBD':26,'ButtonDeckThickness':2,'ButtonDeckTopSetbackTBD':13.6,
 'ButtonPCBWidthTBD':20,'SwitchPCBTopSetbackTBD':10,'SwitchBodyWidthTBD':6,'SwitchBodyHeightTBD':3.5,
 'SwitchActuatorHeightTBD':1.5,'SwitchActuatorDiameterTBD':3.5,'SwitchAirGapTBD':.2,'PusherDiameter':3,
 'ButtonScrewLengthTBD':18,'FixtureWidth':64,'MeasureFixtureWidth':72
}
manufacturer={'EncoderBodyWidth','EncoderBodyHeight','EncoderBodyDepth','BushingDiameter','BushingLength','ShaftDiameter','ShaftFlatSpan','ShaftLength','FlatLength','WasherOD','WasherThickness','NutThickness','NutAF','TerminalPitch','TerminalWidth'}
docs=[];sets={}
def style(o,color,transparency=0):
 o.ViewObject.ShapeColor=color;o.ViewObject.Transparency=transparency
 o.ViewObject.LineColor=(.25,.28,.25)
 if not o.Shape.isNull():
  material=o.ViewObject.ShapeAppearance[0];material.DiffuseColor=color;material.SpecularColor=(0,0,0);material.Shininess=.1
  o.ViewObject.ShapeAppearance=[material]*len(o.Shape.Faces)
def setup(doc,coupon=False):
 p=doc.addObject('Spreadsheet::Sheet','ControlDimensions')
 aliases={}
 for row,(key,value) in enumerate(values.items(),1):
  aliases[key]='B'+str(row);p.set('A'+str(row),key);p.set(aliases[key],str(0 if coupon and key=='PanelBottom' else value)+' mm');p.setAlias(aliases[key],key)
  p.set('C'+str(row),'BOURNS nominal drawing Rev04/26; not measured on owned parts' if key in manufacturer else 'PROVISIONAL measure hardware / process' if key.endswith('TBD') else 'Proposed design dimension')
 formulas={
 'PanelTop':'PanelBottom+PanelThickness','EncoderFront':'PanelBottom-EncoderSetback',
 'EncoderRear':'EncoderFront-EncoderBodyDepth','CarrierTop':'EncoderFront+CarrierThickness',
 'EncoderPCBTop':'EncoderRear-EncoderBoardGapTBD','EncoderPCBBack':'EncoderPCBTop-PCBThicknessTBD',
 'KnobBase':'PanelTop+KnobFaceGap','KnobTop':'KnobBase+KnobHeight','ShaftTop':'EncoderFront+ShaftLength',
 'KnobBoreDepth':'ShaftTop-KnobBase+ShaftTipGapTBD',
 'SwitchPCBTop':'PanelBottom-SwitchPCBTopSetbackTBD','SwitchPCBBack':'SwitchPCBTop-PCBThicknessTBD',
 'SwitchBodyTop':'SwitchPCBTop+SwitchBodyHeightTBD','ActuatorTop':'SwitchBodyTop+SwitchActuatorHeightTBD',
 'CapFlangeBottom':'PanelBottom-CapFlangeThickness','PusherBottom':'ActuatorTop+SwitchAirGapTBD',
 'GuideBottom':'PanelBottom-CapFlangeThickness-TravelStopTBD-StopShelfThickness',
 'DeckTop':'PanelBottom-ButtonDeckTopSetbackTBD','DeckBottom':'DeckTop-ButtonDeckThickness'
 }
 for key,formula in formulas.items():
  row+=1;aliases[key]='B'+str(row);p.set('A'+str(row),key);p.set(aliases[key],'='+formula);p.setAlias(aliases[key],key);p.set('C'+str(row),'Calculated')
 if not coupon:
  p.set(aliases['PanelBottom'],'=Parameters.BaseHeight+Parameters.JointGapTBD');p.set(aliases['PanelThickness'],'=Parameters.PanelThickness')
 p.setColumnWidth('A',235);p.setColumnWidth('C',450)
 construction=doc.addObject('App::DocumentObjectGroup','ControlConstruction')
 printed=doc.addObject('App::DocumentObjectGroup','PrintedControlParts')
 references=doc.addObject('App::DocumentObjectGroup','ControlHardwareReferences')
 reserves=doc.addObject('App::DocumentObjectGroup','ControlClearanceEnvelopes')
 keys=set(values)|set(formulas)
 def ex(o,prop,formula):o.setExpression(prop,re.sub(r'\b('+'|'.join(sorted(keys,key=len,reverse=True))+r')\b',r'ControlDimensions.\1',formula))
 def box(name,w,d,h,x,y,z,group=construction):
  o=doc.addObject('Part::Box',name);group.addObject(o)
  for prop,f in [('Length',w),('Width',d),('Height',h),('Placement.Base.x',x),('Placement.Base.y',y),('Placement.Base.z',z)]:ex(o,prop,f)
  return o
 def cyl(name,r,h,x,y,z,group=construction):
  o=doc.addObject('Part::Cylinder',name);group.addObject(o)
  for prop,f in [('Radius',r),('Height',h),('Placement.Base.x',x),('Placement.Base.y',y),('Placement.Base.z',z)]:ex(o,prop,f)
  return o
 def fuse(name,objects,group=construction):
  o=doc.addObject('Part::MultiFuse',name);group.addObject(o);o.Shapes=objects;o.Refine=True;return o
 def cut(name,base,tool,group=construction):
  o=doc.addObject('Part::Cut',name);group.addObject(o);o.Base=base;o.Tool=tool;o.Refine=True;return o
 def ring(name,od,id,h,x,y,z):return cut(name,cyl(name+'Outside','('+od+')/2',h,x,y,z),cyl(name+'Bore','('+id+')/2','('+h+')+.2 mm',x,y,'('+z+')-.1 mm'))
 def fillet(name,obj,r):
  doc.recompute();top=obj.Shape.BoundBox.ZMax
  edges=[i+1 for i,e in enumerate(obj.Shape.Edges) if abs(e.BoundBox.ZMin-top)<1e-5 and abs(e.BoundBox.ZMax-top)<1e-5]
  o=doc.addObject('Part::Fillet',name);construction.addObject(o);o.Base=obj;o.Edges=[(edges[0],r,r)];return o
 def encoder(name,x,y,phase=False):
  X=lambda s:'('+x+')+('+s+')';Y=lambda s:'('+y+')+('+s+')'
  body=box(name+'Body','EncoderBodyWidth','EncoderBodyHeight','EncoderBodyDepth',X('-EncoderBodyWidth/2'),Y('-EncoderBodyHeight/2'),'EncoderRear',references)
  body.Label=name+' Bourns simplified body - manufacturer nominal'
  bushing=cyl(name+'Bushing','BushingDiameter/2','BushingLength',x,y,'EncoderFront',references)
  bushing.Label='M7 x 0.75 threaded interface envelope - threads not modeled'
  shaft0=cyl(name+'RoundShaft','ShaftDiameter/2','ShaftLength-BushingLength',x,y,'EncoderFront+BushingLength')
  flat=box(name+'ShaftFlatTool','ShaftDiameter','ShaftDiameter*2','FlatLength+.1 mm',X('ShaftFlatSpan-ShaftDiameter/2'),Y('-ShaftDiameter'),'ShaftTop-FlatLength')
  shaft=cut(name+'FlattedShaft',shaft0,flat,references)
  washer=ring(name+'Washer','WasherOD','7.1 mm','WasherThickness',x,y,'CarrierTop');references.addObject(washer)
  nut=ring(name+'NutEnvelope','11.55 mm','BushingDiameter','NutThickness',x,y,'CarrierTop+WasherThickness');references.addObject(nut);nut.Label='M7 x 0.75 nut envelope (10 AF), threads not modeled'
  pcb=box(name+'ConnectionPCB_TBD','EncoderPCBWidthTBD','EncoderPCBDepthTBD','PCBThicknessTBD',X('-EncoderPCBWidthTBD/2'),Y('-EncoderPCBDepthTBD/2'),'EncoderPCBBack',references)
  pcb.Label='Unselected 20 x 24 mm interconnect PCB envelope; no fabricated hole pattern'
  pins=[]
  for i,dx in enumerate([-2.5,0,2.5]):pins.append(box(name+'ACB'+str(i),'TerminalWidth','.5 mm','PinRearReachTBD',X(str(dx-.4)+' mm'),Y('-7.75 mm'),'EncoderRear-PinRearReachTBD',references))
  for i,dx in enumerate([-2.5,2.5]):pins.append(box(name+'UnusedPushPin'+str(i),'.8 mm','.5 mm','PinRearReachTBD',X(str(dx-.4)+' mm'),Y('6.75 mm'),'EncoderRear-PinRearReachTBD',references))
  for i,dx in enumerate([-6.6,6.6]):pins.append(box(name+'MountTab'+str(i),'1.8 mm','2.6 mm','PinRearReachTBD',X(str(dx-.9)+' mm'),Y('-1.3 mm'),'EncoderRear-PinRearReachTBD',references))
  for pin in pins:pin.Label=pin.Name+' drawing XY / provisional Z reach (unconnected tabs/push terminals)'
  wires=box(name+'RearWiringTBD','EncoderPCBWidthTBD','EncoderPCBDepthTBD','EncoderWireDepthTBD',X('-EncoderPCBWidthTBD/2'),Y('-EncoderPCBDepthTBD/2'),'EncoderPCBBack-EncoderWireDepthTBD',reserves)
  blank=box(name+'CarrierPlate','CarrierWidth','CarrierDepth','CarrierThickness',X('-CarrierWidth/2'),Y('-CarrierDepth/2'),'EncoderFront')
  skirt=box(name+'SkirtOutside','EncoderBodyWidth+2*BodySideGapTBD+4 mm','EncoderBodyHeight+2*BodySideGapTBD+4 mm','BodySkirtDepth',X('-EncoderBodyWidth/2-BodySideGapTBD-2 mm'),Y('-EncoderBodyHeight/2-BodySideGapTBD-2 mm'),'EncoderFront-BodySkirtDepth')
  hollow=box(name+'BodyRelief','EncoderBodyWidth+2*BodySideGapTBD','EncoderBodyHeight+2*BodySideGapTBD','BodySkirtDepth+.1 mm',X('-EncoderBodyWidth/2-BodySideGapTBD'),Y('-EncoderBodyHeight/2-BodySideGapTBD'),'EncoderFront-BodySkirtDepth-.1 mm')
  skirt=cut(name+'BodyAntiRotationPocket',skirt,hollow)
  bores=[cyl(name+'BushingOpening','BushingBoreTBD/2','CarrierThickness+.2 mm',x,y,'EncoderFront-.1 mm')]
  posts=[];pilots=[]
  for i,(sx,sy) in enumerate([(-1,-1),(-1,1),(1,-1),(1,1)]):
   xx=X(str(sx)+'*EncoderMountX');yy=Y(str(sy)+'*EncoderMountY')
   bores.append(cyl(name+'MountClearance'+str(i),'MountBoreTBD/2','CarrierThickness+.2 mm',xx,yy,'EncoderFront-.1 mm'))
   posts.append(cyl(name+'PanelPost'+str(i),'3.2 mm','PanelBottom-CarrierTop',xx,yy,'CarrierTop'))
   pilots.append(cyl(name+'PanelPilot'+str(i),'MountPilotTBD/2','7 mm',xx,yy,'CarrierTop'))
  carrier=cut(name+'RearBulkhead',fuse(name+'CarrierBlank',[blank,skirt]),fuse(name+'CarrierTools',bores),printed)
  cap0=cyl(name+'KnobBlank','KnobDiameter/2','KnobHeight',x,y,'KnobBase')
  cap0=fillet(name+'KnobRounded',cap0,values['KnobRounding'])
  bore=cyl(name+'KnobRoundBore','ShaftBoreDiameterTBD/2','KnobBoreDepth+.1 mm',x,y,'KnobBase-.1 mm')
  boreflat=box(name+'BoreFlatTool','ShaftBoreDiameterTBD','ShaftBoreDiameterTBD*2','KnobBoreDepth+.3 mm',X('ShaftFlatSpan-ShaftDiameter/2+ShaftFlatGapTBD'),Y('-ShaftBoreDiameterTBD'),'KnobBase-.2 mm')
  bore=cut(name+'KnobDBore',bore,boreflat)
  screw=cyl(name+'RadialScrewAccess','KnobScrewBoreTBD/2','KnobDiameter/2',X('ShaftFlatSpan-ShaftDiameter/2'),y,'KnobBase+KnobScrewHeight');screw.Placement.Rotation=App.Rotation(App.Vector(0,1,0),90)
  trap=box(name+'CaptiveNutSlot','NutTrapDepthTBD','NutTrapWidthTBD','KnobScrewHeight+NutTrapHeightTBD/2',X('NutTrapX-NutTrapDepthTBD/2'),Y('-NutTrapWidthTBD/2'),'KnobBase-.1 mm')
  grub=cyl(name+'M3x16ScrewEnvelope','1.5 mm','16 mm',X('ShaftFlatSpan-ShaftDiameter/2'),y,'KnobBase+KnobScrewHeight',references);grub.Placement.Rotation=App.Rotation(App.Vector(0,1,0),90)
  grub.Label='Candidate M3 x 16 grub screw envelope - threads/retention unqualified'
  clampnut=doc.addObject('Part::Prism',name+'M3NutBlank');construction.addObject(clampnut);clampnut.Polygon=6;clampnut.Circumradius=5.5/math.sqrt(3);clampnut.Height=2.4
  ex(clampnut,'Placement.Base.x',X('NutTrapX-1.2 mm'));ex(clampnut,'Placement.Base.y',y);ex(clampnut,'Placement.Base.z','KnobBase+KnobScrewHeight');clampnut.Placement.Rotation=App.Rotation(App.Vector(0,1,0),90)
  nutbore=cyl(name+'M3NutBore','1.5 mm','2.6 mm',X('NutTrapX-1.3 mm'),y,'KnobBase+KnobScrewHeight');nutbore.Placement.Rotation=App.Rotation(App.Vector(0,1,0),90)
  clampnut=cut(name+'M3NutEnvelope',clampnut,nutbore,references);clampnut.Label='Candidate M3 hex nut 5.5 AF x 2.4 - verify actual hardware'
  grooves=[]
  for i,yy in enumerate([12] if not phase else [10,13]):
   groove=cyl(name+'TactileGroove'+str(i),'.7 mm','6 mm',X('-3 mm'),Y(str(yy)+' mm'),'KnobTop');groove.Placement.Rotation=App.Rotation(App.Vector(0,1,0),90);grooves.append(groove)
  knob=cut(name+'RemovableKnob',cap0,fuse(name+'KnobTools',[bore,screw,trap]+grooves),printed)
  knob.Label=name+' removable rounded knob - '+('two grooves / Phase' if phase else 'one groove / Balance')
  for o in [carrier]:style(o,(.70,.72,.62))
  style(knob,(.44,.59,.48) if not phase else (.44,.56,.65))
  for o in [body,pcb]:style(o,(.22,.33,.26))
  for o in [bushing,shaft,washer,nut,grub,clampnut]+pins:style(o,(.55,.55,.50))
  return {'printed':[carrier,knob],'references':[body,bushing,shaft,washer,nut,pcb,grub,clampnut]+pins,'reserve':[wires],'posts':posts,'pilots':pilots,'knob':knob,'carrier':carrier}
 def button(name,x,y,diam):
  X=lambda s:'('+x+')+('+s+')';Y=lambda s:'('+y+')+('+s+')';R='('+diam+')/2'
  shank=cyl(name+'CapBlank',R,'PanelThickness+CapAboveFace+CapFlangeThickness',x,y,'CapFlangeBottom')
  shank=fillet(name+'CapRounded',shank,values['CapRounding'])
  flange=cyl(name+'CaptiveFlange','('+diam+'+CapFlangeExtra)/2','CapFlangeThickness',x,y,'CapFlangeBottom')
  pusher=cyl(name+'Pusher','PusherDiameter/2','CapFlangeBottom-PusherBottom',x,y,'PusherBottom')
  cap=fuse(name+'CaptiveCap',[shank,flange,pusher],printed)
  outer=ring(name+'GuideSleeve',diam+'+CapFlangeExtra+2*GuideRadialGapTBD+2*GuideWall',diam+'+CapFlangeExtra+2*GuideRadialGapTBD','PanelBottom-GuideBottom',x,y,'GuideBottom')
  shelf=ring(name+'TravelStop',diam+'+CapFlangeExtra+2*GuideRadialGapTBD+2*GuideWall',diam+'+2*GuideRadialGapTBD','StopShelfThickness',x,y,'GuideBottom')
  ears=[];holes=[];pilots=[];columns=[];deckparts=[]
  for i,sign in enumerate([-1,1]):
   xx=X(str(sign)+'*('+R+'+GuideEarExtra)')
   ears.append(cyl(name+'GuideEar'+str(i),'GuideEarDiameter/2','PanelBottom-GuideBottom',xx,y,'GuideBottom'))
   # Connect ears to ring with positive overlap; all at rear of panel.
   exx=X('-('+R+'+GuideEarExtra)') if sign<0 else x
   ears.append(box(name+'GuideArm'+str(i),R+'+GuideEarExtra','4 mm','PanelBottom-GuideBottom',exx,Y('-2 mm'),'GuideBottom'))
   holes.append(cyl(name+'StackBore'+str(i),'MountBoreTBD/2','PanelBottom-DeckBottom+.2 mm',xx,y,'DeckBottom-.1 mm'))
   pilots.append(cyl(name+'PanelPilot'+str(i),'MountPilotTBD/2','4 mm',xx,y,'PanelBottom'))
   columns.append(cyl(name+'CarrierColumn'+str(i),'GuideEarDiameter/2','GuideBottom-DeckTop',xx,y,'DeckTop'))
   deckparts.append(box(name+'DeckArm'+str(i),R+'+GuideEarExtra','7 mm','ButtonDeckThickness',exx,Y('-3.5 mm'),'DeckBottom'))
  # Arms must not fill the cap's travel cavity: subtract it after the union.
  cavity=cyl(name+'FlangeMotionCavity','('+diam+'+CapFlangeExtra+2*GuideRadialGapTBD)/2','PanelBottom-(GuideBottom+StopShelfThickness)+.1 mm',x,y,'GuideBottom+StopShelfThickness')
  guideblank=cut(name+'GuideCavityCut',fuse(name+'GuideBlank',[outer,shelf]+ears),cavity)
  stopOpening=cyl(name+'StopCentralOpening','('+diam+'+2*GuideRadialGapTBD)/2','PanelBottom-GuideBottom+.2 mm',x,y,'GuideBottom-.1 mm')
  guideblank=cut(name+'GuideStopOpening',guideblank,stopOpening)
  guide=cut(name+'RearGuideAndStop',guideblank,fuse(name+'GuideBores',holes),printed)
  pcb=box(name+'SwitchPCB_TBD','ButtonPCBWidthTBD','ButtonPCBWidthTBD','PCBThicknessTBD',X('-ButtonPCBWidthTBD/2'),Y('-ButtonPCBWidthTBD/2'),'SwitchPCBBack',references)
  body=box(name+'TactileSwitch_TBD','SwitchBodyWidthTBD','SwitchBodyWidthTBD','SwitchBodyHeightTBD',X('-SwitchBodyWidthTBD/2'),Y('-SwitchBodyWidthTBD/2'),'SwitchPCBTop',references)
  actuator=cyl(name+'Actuator_TBD','SwitchActuatorDiameterTBD/2','SwitchActuatorHeightTBD',x,y,'SwitchBodyTop',references)
  pins=[]
  for i,(xx,yy) in enumerate([(-3.5,-2.25),(-3.5,2.25),(3.5,-2.25),(3.5,2.25)]):
   pins.append(box(name+'Pin_TBD'+str(i),'.5 mm','.5 mm','3.6 mm',X(str(xx-.25)+' mm'),Y(str(yy-.25)+' mm'),'SwitchPCBBack-2 mm',references))
  deckparts.append(box(name+'Deck','ButtonDeckWidthTBD','ButtonDeckWidthTBD','ButtonDeckThickness',X('-ButtonDeckWidthTBD/2'),Y('-ButtonDeckWidthTBD/2'),'DeckBottom'))
  # Support the PCB directly beneath the switch and at edges, clear of assumed pins.
  deckparts.append(box(name+'CentralLoadPedestal','4 mm','4 mm','SwitchPCBBack-DeckTop',X('-2 mm'),Y('-2 mm'),'DeckTop'))
  for i,(xx,yy) in enumerate([(-8.5,-8.5),(-8.5,8.5),(8.5,-8.5),(8.5,8.5)]):
   deckparts.append(box(name+'PCBSupport'+str(i),'3 mm','3 mm','SwitchPCBBack-DeckTop',X(str(xx-1.5)+' mm'),Y(str(yy-1.5)+' mm'),'DeckTop'))
  # Two edge rebates locate an undrilled board; rear clips remain a measured-design gate.
  for i,xx in enumerate([-11.5,10]):deckparts.append(box(name+'BoardEdgeRail'+str(i),'1.5 mm','ButtonPCBWidthTBD','SwitchPCBTop-DeckTop',X(str(xx)+' mm'),Y('-ButtonPCBWidthTBD/2'),'DeckTop'))
  clipbores=[];clippilots=[];clips=[]
  for i,yy in enumerate([-9.5,9.5]):
   clip=box(name+'PCBClipBlank'+str(i),'25 mm','3 mm','1.2 mm',X('-12.5 mm'),Y(str(yy-1.5)+' mm'),'SwitchPCBTop')
   localbores=[]
   for j,xx in enumerate([-11.5,11.5]):
    deckparts.append(cyl(name+'ClipPost'+str(i)+str(j),'1.5 mm','SwitchPCBTop-DeckTop',X(str(xx)+' mm'),Y(str(yy)+' mm'),'DeckTop'))
    localbores.append(cyl(name+'ClipBore'+str(i)+str(j),'1.1 mm','1.4 mm',X(str(xx)+' mm'),Y(str(yy)+' mm'),'SwitchPCBTop-.1 mm'))
    clippilots.append(cyl(name+'ClipPilot'+str(i)+str(j),'.75 mm','4.5 mm',X(str(xx)+' mm'),Y(str(yy)+' mm'),'SwitchPCBTop-4.5 mm'))
   clip=cut(name+'RemovablePCBClip'+str(i),clip,fuse(name+'ClipTools'+str(i),localbores),printed);clips.append(clip);style(clip,(.62,.65,.56))
  holes=holes+clippilots
  carrier=cut(name+'SupportedSwitchCarrier',fuse(name+'SwitchCarrierBlank',deckparts+columns),fuse(name+'CarrierBores',holes),printed)
  opening=cyl(name+'FaceOpening','('+diam+'+2*GuideRadialGapTBD)/2','PanelThickness+.2 mm',x,y,'PanelBottom-.1 mm')
  wire=box(name+'RearSolderWire_TBD','ButtonPCBWidthTBD','ButtonPCBWidthTBD','2 mm',X('-ButtonPCBWidthTBD/2'),Y('-ButtonPCBWidthTBD/2'),'SwitchPCBBack-2 mm',reserves)
  cap.Label=name+' captive cap - travel/actuation provisional'
  carrier.Label=name+' load-supported switch carrier - PCB clip contacts/pilots provisional'
  style(cap,(.66,.42,.32) if name.startswith('Measure') else (.67,.58,.35) if name.startswith(('Reset','Colors')) else (.48,.60,.52))
  for o in [guide,carrier]:style(o,(.72,.74,.65))
  for o in [pcb,body,actuator]+pins:style(o,(.25,.31,.27))
  return {'printed':[cap,guide,carrier]+clips,'references':[pcb,body,actuator]+pins,'reserve':[wire],'posts':[],'pilots':pilots,'opening':opening,'cap':cap,'guide':guide,'carrier':carrier}
 return dict(p=p,aliases=aliases,ex=ex,box=box,cyl=cyl,fuse=fuse,cut=cut,encoder=encoder,button=button,printed=printed,references=references,reserves=reserves,construction=construction)

S=setup(assembly);systems=[]
for name,x in [('Balance','58 mm'),('Phase','150 mm')]:systems.append(S['encoder'](name,x,'108 mm',name=='Phase'))
buttons=[('X',32,65,'GateDiameter'),('Y',80,65,'GateDiameter'),('Z',128,65,'GateDiameter'),('H',176,65,'GateDiameter'),('Measure',104,28,'MeasureDiameter'),('Reset',40,28,'SecondaryDiameter'),('Colors',168,28,'SecondaryDiameter')]
for name,x,y,diam in buttons:systems.append(S['button'](name,str(x)+' mm',str(y)+' mm',diam))
base=S['fuse']('FrontWithEncoderPosts',[assembly.LCDIntegratedFrontHousing]+[o for sys in systems for o in sys['posts']])
tools=S['fuse']('ControlFaceTools',[o for sys in systems for o in sys['pilots']]+[sys['opening'] for sys in systems if 'opening' in sys])
front=S['cut']('ControlsFrontHousing',base,tools,S['printed']);style(front,(.86,.81,.70))
assembly.LCDIntegratedFrontHousing.Visibility=False
for o in assembly.DiscoveryControls.Group:o.Visibility=False
for name in ['ProbabilityEncoderTBD','PhaseEncoderTBD']+[b[0]+'SwitchTBD' for b in buttons]:assembly.getObject(name).Visibility=False
docs.append(assembly);sets[assembly.Name]=(S,systems,[front]+[o for sys in systems for o in sys['printed']])

for kind,path in zip(['Encoder','Gate','Measure'],outputs[1:]):
 d=App.newDocument('MFQ_'+kind+'_Fixture');d.Label=kind+' fixture - '+('manufacturer nominal / verify hardware' if kind=='Encoder' else 'PROVISIONAL switch - STL release blocked')
 F=setup(d,True);width='MeasureFixtureWidth' if kind=='Measure' else 'FixtureWidth';center='('+width+')/2'
 sys=F['encoder']('Balance',center,center) if kind=='Encoder' else F['button'](kind,center,center,'MeasureDiameter' if kind=='Measure' else 'GateDiameter')
 panel=F['box'](kind+'PanelBlank',width,width,'PanelThickness','0 mm','0 mm','PanelBottom')
 holes=list(sys['pilots'])
 if kind=='Encoder':holes.append(F['cyl']('ShaftPassage','4.5 mm','PanelThickness+.2 mm',center,center,'PanelBottom-.1 mm'))
 else:holes.append(sys['opening'])
 plate=F['fuse'](kind+'PanelWithPosts',[panel]+sys['posts']) if sys['posts'] else panel
 panel=F['cut'](kind+'TestPanel',plate,F['fuse'](kind+'PanelTools',holes),F['printed']);style(panel,(.86,.81,.70))
 d.recompute();d.saveAs(str(path));docs.append(d);sets[d.Name]=(F,[sys],[panel]+sys['printed'])

for d,path in zip(docs,outputs):
 F,ss,parts=sets[d.Name]
 d.recompute()
 for o in F['construction'].Group:o.Visibility=False
 for o in F['reserves'].Group:o.Visibility=False
 for o in F['references'].Group:o.Visibility=True
 for o in parts:o.Visibility=True
 if d==assembly:d.save()
 else:d.save()

report={'manufacturer_source':'https://www.bourns.com/docs/product-datasheets/pec11r.pdf','manufacturer_revision':'04/26','physical_dimensions_verified':False,'preserved_sha256':hashes,'invalid':[],'collisions':[],'reopen_errors':[],'parameter_checks':[],'documents':[],'print_release':{'encoder':'nominal mechanical calibration only; verify real hardware and clamp nut first','buttons':'BLOCKED: actual switch height/travel/footprint and PCB retention not measured'}}
for d in docs:
 F,ss,parts=sets[d.Name]
 for obj in parts:
  if not obj.Shape.isValid() or len(obj.Shape.Solids)!=1 or not obj.Shape.isClosed():report['invalid'].append([d.Name,obj.Name])
 for i,a in enumerate(parts):
  for b in parts[i+1:]:
   vol=a.Shape.common(b.Shape).Volume
   if vol>.001:report['collisions'].append([d.Name,a.Name,b.Name,vol])
 report['documents'].append({'file':Path(d.FileName).relative_to(root).as_posix(),'printed_parts':[o.Name for o in parts]})
 # Alter real native dimension, confirm knob or button carrier changes, restore.
 p=F['p'];alias='KnobDiameter' if 'knob' in ss[0] else 'TravelStopTBD';cell=p.getCellFromAlias(alias);old=p.getContents(cell)
 obj=ss[0]['knob'] if 'knob' in ss[0] else ss[0]['guide'];before=obj.Shape.Volume
 p.set(cell,str(values[alias]+.2)+' mm');d.recompute();after=obj.Shape.Volume
 report['parameter_checks'].append([d.Label,alias,abs(after-before)>1e-6])
 p.set(cell,old);d.recompute();d.save()

def shot(d,path,q):
 App.setActiveDocument(d.Name);v=Gui.activeDocument().activeView();v.setCameraType('Orthographic');v.getCameraNode().orientation.setValue(coin.SbRotation(*q));Gui.Selection.clearSelection();Gui.updateGui();v.fitAll();Gui.updateGui();v.saveImage(str(path),1600,1250,'White')
ax=(.3647051996310009,.2798481423331213,.11591689595929514,.8804762392171493)
shot(assembly,cad/'controls-prototype-top.png',(0,0,0,1));shot(assembly,cad/'controls-prototype-axonometric.png',ax)
for d,kind in zip(docs[1:],['encoder','gate','measure']):
 shot(d,cad/(kind+'-fixture-assembled.png'),ax)
 review=App.newDocument('ControlExplodedReview')
 F,ss,parts=sets[d.Name]
 for i,obj in enumerate(parts):
  o=review.addObject('Part::Feature','Exploded'+str(i));shape=obj.Shape.copy();shape.translate(App.Vector(i*4,0,(len(parts)-i)*15));o.Shape=shape;style(o,obj.ViewObject.ShapeColor)
 review.recompute();shot(review,cad/(kind+'-fixture-exploded.png'),ax);App.closeDocument(review.Name)
 review=App.newDocument('ControlSectionReview');half=Part.makeBox(100,100,100,App.Vector(32 if kind!='measure' else 36,-10,-50))
 for i,obj in enumerate(parts+ss[0]['references']):
  shape=obj.Shape.common(half)
  if not shape.isNull():o=review.addObject('Part::Feature','Section'+str(i));o.Shape=shape;style(o,obj.ViewObject.ShapeColor)
 review.recompute();shot(review,cad/(kind+'-fixture-section.png'),(.5,-.5,-.5,.5));App.closeDocument(review.Name)

for d in docs:App.closeDocument(d.Name)
for path in outputs:
 d=App.openDocument(str(path));d.recompute()
 for o in d.Objects:
  if 'Invalid' in o.State:report['reopen_errors'].append([path.name,o.Name,str(o.State)])
for path,digest in hashes.items():assert hashlib.sha256((root/path).read_bytes()).hexdigest()==digest,path
report['prior_files_unchanged']=True
(cad/'controls-prototype-validation.json').write_text(json.dumps(report,indent=2)+'\n')
settings.SetInt('CountBackupFiles',backups)
print(json.dumps({k:v for k,v in report.items() if k!='preserved_sha256'},indent=2))
App.setActiveDocument(App.getDocument('MyFirstQubit_iteration03_controls_prototype').Name if 'MyFirstQubit_iteration03_controls_prototype' in App.listDocuments() else d.Name)
Gui.activeDocument().activeView().fitAll()
