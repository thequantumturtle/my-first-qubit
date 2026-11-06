"""FreeCAD MCP entry point: reversible LCD integration + independent fit coupon.
Model-derived hole locations are working references, not caliper measurements.
"""
from pathlib import Path
import json,hashlib,re,math,csv
import Part
from pivy import coin
root=Path(r'C:\Users\djust\OneDrive\Documents\GitHub\my-first-qubit')
cad=root/'enclosure/freecad'
assemblyFile=cad/'MyFirstQubit_iteration03_LCD_mechanical_integration.FCStd'
fitFile=cad/'MyFirstQubit_LCD_fit_test.FCStd'
if assemblyFile.exists() or fitFile.exists():raise RuntimeError('New revision already exists; refusing overwrite')
protected=list(cad.glob('*.FCStd'))+list((root/'hardware/models').rglob('*'))
protected=[f for f in protected if f.is_file()]
hashes={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in protected}
source=cad/'MyFirstQubit_iteration03_candidate_LCD.FCStd'
src=next((d for d in App.listDocuments().values() if Path(d.FileName)==source),None)
if src is None:src=App.openDocument(str(source))
src.saveCopy(str(assemblyFile));assembly=App.openDocument(str(assemblyFile))
assembly.Label='Iteration 03 - serviceable LCD mounts, user-reported mechanical match'
component=assembly.LeftCandidateLCD.LinkedObject
componentDoc=component.Document

baseValues={
 'PanelBottom':30.3,'PanelThickness':5,'LensRecess':1,'LensThicknessTBD':1.5,
 'LensGapTargetTBD':2,'ApertureDiameterTBD':34,'LensDiameterTBD':38,
 'LensPocketDiameterTBD':38.6,'NoseOuterDiameterTBD':38.4,'OpticalBoreDiameter':36.4,
 'RingOuterDiameter':48,'FlangeBoreDiameter':40.6,'FlangeThickness':1.5,
 'ShoulderThickness':0.7,'ShoulderPocketDiameter':49,
 'NeckNotchWidth':22,'NeckNotchDepth':10,'NeckNotchY':-30,
 'BoardNeckReliefWidth':32,'BoardNeckReliefDepth':18,
 'LensScrewX':25,'LensTabDiameter':7,'ScrewClearanceTBD':2.4,'PilotDiameterTBD':1.6,
 'PCBPilotDepthTBD':5,'LensPilotDepthTBD':3.5,'PCBPostDiameter':4.6,
 'SourcePCBFrontSetback':1.999998526721,'SourcePCBThickness':0.41148,
 'SourceHolePitch':23,'SourceHoleCenterX':0.279993591309,
 'SourceHoleY':-23.726002144678,'SourceHeaderCenterX':0.28003692627,
 'SourceHeaderCenterY':-24.455921237, 'HeaderReliefWidthTBD':19,'HeaderReliefDepthTBD':5,
 'HeaderReliefHeightTBD':2.2,'ExtraConnectorRearReserveTBD':6,
 'SolderHeightTBD':1,'BracketRearGapTBD':1.2,'BracketThickness':2,
 'BracketOuterWidth':52,'RailWidth':3,'RailBottomY':-24,'RailTopY':21,
 'TopRailWidth':3,'NeckBridgeY':-19.5,'NeckBridgeWidth':3,
 'NeckClampDiameter':4.4,'BackPadX':12,'BackPadY':12,'BackPadDiameter':4,
 'ContactKeepoutMarginTBD':0.2,'M2ShankDiameterTBD':2,'M2HeadDiameterTBD':3.8,
 'M2HeadHeightTBD':1.5,'PCBScrewLengthTBD':8,'LensScrewLengthTBD':4,
 'DriverDiameterTBD':4,'DriverReachTBD':10,
 'CouponWidth':64,'CouponDepth':68,'CouponCornerRadius':5,'CouponCenterX':32,'CouponCenterY':36
}

def setup(doc,coupon=False):
 p=doc.addObject('Spreadsheet::Sheet','LCDMountParameters')
 p.Label='LCD dimensions: user match / source nominal / design / unmeasured TBD'
 vals=dict(baseValues)
 if coupon:vals['PanelBottom']=0
 aliases={}
 sourceKeys={k for k in vals if k.startswith('Source')}
 for row,(key,val) in enumerate(vals.items(),1):
  aliases[key]='B'+str(row);p.set('A'+str(row),key);p.set('B'+str(row),('=' if val<0 else '')+str(val)+' mm');p.setAlias('B'+str(row),key)
  p.set('C'+str(row),'SOURCE MODEL: working reference; numerical physical measurement not supplied' if key in sourceKeys else 'PROVISIONAL: verify by measurement/fit/loads' if key.endswith('TBD') else 'Proposed design choice')
 p.setColumnWidth('A',240);p.setColumnWidth('B',110);p.setColumnWidth('C',480)
 if not coupon:
  for key,formula in [('PanelBottom','=Parameters.BaseHeight+Parameters.JointGapTBD'),('PanelThickness','=Parameters.PanelThickness'),('LensRecess','=Parameters.LensRecess'),('LensThicknessTBD','=Parameters.LensThicknessTBD'),('ApertureDiameterTBD','=Parameters.LCDOpeningTBD'),('LensDiameterTBD','=Parameters.LensDiameterTBD'),('LensPocketDiameterTBD','=Parameters.LensDiameterTBD+2*Parameters.LensRadialClearanceTBD')]:p.set(aliases[key],formula)
 # Calculated stack parameters remain live when lens gap or PCB stack changes.
 formulas={
  'PanelTop':'PanelBottom+PanelThickness',
  'LensBottom':'PanelTop-LensRecess-LensThicknessTBD',
  'DisplayFront':'LensBottom-LensGapTargetTBD',
  'PCBFront':'DisplayFront-SourcePCBFrontSetback',
  'PCBBack':'PCBFront-SourcePCBThickness',
  'BracketTop':'PCBBack-BracketRearGapTBD',
  'BracketBottom':'BracketTop-BracketThickness',
  'FlangeBottom':'PanelBottom-FlangeThickness',
  'ShoulderTop':'PanelBottom+ShoulderThickness',
  'NoseHeight':'LensBottom-ShoulderTop',
  'HoleLeftX':'SourceHoleCenterX-SourceHolePitch/2',
  'HoleRightX':'SourceHoleCenterX+SourceHolePitch/2'
 }
 for key,formula in formulas.items():
  row+=1;p.set('A'+str(row),key);p.set('B'+str(row),'='+formula);p.setAlias('B'+str(row),key);p.set('C'+str(row),'Calculated stack')
 keys=set(vals)|set(formulas)
 def ex(o,prop,s):
  s=re.sub(r'\b('+'|'.join(sorted(keys,key=len,reverse=True))+r')\b',r'LCDMountParameters.\1',s)
  o.setExpression(prop,s)
 construction=doc.addObject('App::DocumentObjectGroup','LCDMountConstruction')
 fabricated=doc.addObject('App::DocumentObjectGroup','LCDMountParts')
 fasteners=doc.addObject('App::DocumentObjectGroup','FastenerEnvelopes')
 reserves=doc.addObject('App::DocumentObjectGroup','LCDServiceKeepouts')
 def box(name,w,d,h,x,y,z,group=construction):
  o=doc.addObject('Part::Box',name);group.addObject(o)
  for prop,s in [('Length',w),('Width',d),('Height',h),('Placement.Base.x',x),('Placement.Base.y',y),('Placement.Base.z',z)]:ex(o,prop,s)
  return o
 def cyl(name,r,h,x,y,z,group=construction):
  o=doc.addObject('Part::Cylinder',name);group.addObject(o)
  for prop,s in [('Radius',r),('Height',h),('Placement.Base.x',x),('Placement.Base.y',y),('Placement.Base.z',z)]:ex(o,prop,s)
  return o
 def union(name,objects,group=construction):
  o=doc.addObject('Part::MultiFuse',name);group.addObject(o);o.Shapes=objects;o.Refine=True;return o
 def cut(name,base,tool,group=construction):
  o=doc.addObject('Part::Cut',name);group.addObject(o);o.Base=base;o.Tool=tool;o.Refine=True;return o
 def annulus(name,od,id,h,x,y,z):
  return cut(name,cyl(name+'Outer','('+od+')/2',h,x,y,z),cyl(name+'Bore','('+id+')/2','('+h+')+0.2 mm',x,y,'('+z+')-0.1 mm'))
 def rounded(name,w,d,r,h,x,y,z):
  objects=[box(name+'WebX','('+w+')-2*('+r+')',d,h,'('+x+')+('+r+')',y,z),box(name+'WebY',w,'('+d+')-2*('+r+')',h,x,'('+y+')+('+r+')',z)]
  for i,(xx,yy) in enumerate([('('+x+')+('+r+')','('+y+')+('+r+')'),('('+x+')+('+w+')-('+r+')','('+y+')+('+r+')'),('('+x+')+('+r+')','('+y+')+('+d+')-('+r+')'),('('+x+')+('+w+')-('+r+')','('+y+')+('+d+')-('+r+')')]):objects.append(cyl(name+'C'+str(i),r,h,xx,yy,z))
  return union(name,objects)
 def add_system(side,cx,cy):
  def X(v='0 mm'):return '('+cx+')+('+v+')'
  def Y(v='0 mm'):return '('+cy+')+('+v+')'
  # Ring: wide PCB-clearing flange, pocketed shoulder, thin full lens-bearing nose.
  flange=annulus(side+'Flange','RingOuterDiameter','FlangeBoreDiameter','FlangeThickness',cx,cy,'FlangeBottom')
  shoulder=annulus(side+'Shoulder','RingOuterDiameter','OpticalBoreDiameter','ShoulderThickness',cx,cy,'PanelBottom')
  nose=annulus(side+'Nose','NoseOuterDiameterTBD','OpticalBoreDiameter','NoseHeight',cx,cy,'ShoulderTop')
  tabs=[cyl(side+'RingTab'+str(i),'LensTabDiameter/2','FlangeThickness',X(s+'LensScrewX'),cy,'FlangeBottom') for i,s in enumerate(['-',''])]
  ringBlank=union(side+'LensRingBlank',[flange,shoulder,nose]+tabs)
  notch=box(side+'HeaderNotch','NeckNotchWidth','NeckNotchDepth','PanelThickness+FlangeThickness',X('-NeckNotchWidth/2'),Y('NeckNotchY'),'FlangeBottom')
  neckClearance=box(side+'BoardNeckRelief','BoardNeckReliefWidth','BoardNeckReliefDepth','FlangeThickness',X('-BoardNeckReliefWidth/2'),Y('NeckNotchY'),'FlangeBottom')
  ringBores=[cyl(side+'RingScrewBore'+str(i),'ScrewClearanceTBD/2','FlangeThickness+0.2 mm',X(s+'LensScrewX'),cy,'FlangeBottom-0.1 mm') for i,s in enumerate(['-',''])]
  ring=cut(side+'LensRetainer',ringBlank,union(side+'RingTools',[notch,neckClearance]+ringBores),fabricated)
  ring.Label=side+' removable lens ring - M2 proposal, retention unvalidated'
  # PCB supports at the actual modeled hole axes, not inferred symmetric LCD center.
  posts=[];pilots=[];contacts=[]
  for i,hx in enumerate(['HoleLeftX','HoleRightX']):
   posts.append(cyl(side+'PCBStandoff'+str(i),'PCBPostDiameter/2','PanelBottom-PCBFront',X(hx),Y('SourceHoleY'),'PCBFront'))
   pilots.append(cyl(side+'PCBBlindPilot'+str(i),'PilotDiameterTBD/2','PCBPilotDepthTBD',X(hx),Y('SourceHoleY'),'PCBFront'))
  pilots += [cyl(side+'RingBlindPilot'+str(i),'PilotDiameterTBD/2','LensPilotDepthTBD',X(s+'LensScrewX'),cy,'PanelBottom') for i,s in enumerate(['-',''])]
  pocket=cyl(side+'ShoulderPocket','ShoulderPocketDiameter/2','ShoulderThickness+0.05 mm',cx,cy,'PanelBottom-0.05 mm')
  relief=box(side+'HeaderRelief','HeaderReliefWidthTBD','HeaderReliefDepthTBD','HeaderReliefHeightTBD+0.05 mm',X('SourceHeaderCenterX-HeaderReliefWidthTBD/2'),Y('SourceHeaderCenterY-HeaderReliefDepthTBD/2'),'PanelBottom-0.05 mm')
  # Replaceable rear cradle: rails outside board, backside pads at four areas only.
  plates=[box(side+'Rail'+str(i),'RailWidth','RailTopY-RailBottomY','BracketThickness',X(v),Y('RailBottomY'),'BracketBottom') for i,v in enumerate(['-BracketOuterWidth/2','BracketOuterWidth/2-RailWidth'])]
  plates.append(box(side+'UpperBridge','BracketOuterWidth','TopRailWidth','BracketThickness',X('-BracketOuterWidth/2'),Y('RailTopY-TopRailWidth'),'BracketBottom'))
  plates.append(box(side+'NeckBridge','BracketOuterWidth','NeckBridgeWidth','BracketThickness',X('-BracketOuterWidth/2'),Y('NeckBridgeY-NeckBridgeWidth/2'),'BracketBottom'))
  for i,hx in enumerate(['HoleLeftX','HoleRightX']):
   plates.append(cyl(side+'NeckPadBase'+str(i),'NeckClampDiameter/2','BracketThickness',X(hx),Y('SourceHoleY'),'BracketBottom'))
   plates.append(box(side+'NeckPadArm'+str(i),'NeckClampDiameter','NeckBridgeY-SourceHoleY','BracketThickness',X(hx+'-NeckClampDiameter/2'),Y('SourceHoleY'),'BracketBottom'))
   pad=cyl(side+'NeckContactPad'+str(i),'NeckClampDiameter/2','BracketRearGapTBD',X(hx),Y('SourceHoleY'),'BracketTop');contacts.append(pad)
  for i,sign in enumerate(['-','']):
   left='-BracketOuterWidth/2' if sign=='-' else 'BackPadX'
   plates.append(box(side+'BackPadArm'+str(i),'BracketOuterWidth/2-BackPadX','BackPadDiameter','BracketThickness',X(left),Y('BackPadY-BackPadDiameter/2'),'BracketBottom'))
   plates.append(cyl(side+'BackPadBase'+str(i),'BackPadDiameter/2','BracketThickness',X(sign+'BackPadX'),Y('BackPadY'),'BracketBottom'))
   pad=cyl(side+'BackContactPad'+str(i),'BackPadDiameter/2','BracketRearGapTBD',X(sign+'BackPadX'),Y('BackPadY'),'BracketTop');contacts.append(pad)
  cradleBlank=union(side+'CradleBlank',plates+contacts)
  cradleHoles=[cyl(side+'CradleClearance'+str(i),'ScrewClearanceTBD/2','BracketThickness+BracketRearGapTBD+0.2 mm',X(hx),Y('SourceHoleY'),'BracketBottom-0.1 mm') for i,hx in enumerate(['HoleLeftX','HoleRightX'])]
  cradle=cut(side+'LCDCradle',cradleBlank,union(side+'CradleHoleTools',cradleHoles),fabricated)
  cradle.Label=side+' screw-removable LCD cradle - verify four backside contact lands'
  # Fasteners are envelope concepts only; threads/washers/selected specifications TBD.
  screws=[]
  for family,xs,y,z,length in [('PCB',['HoleLeftX','HoleRightX'],'SourceHoleY','BracketBottom','PCBScrewLengthTBD'),('Lens',['-LensScrewX','LensScrewX'],'0 mm','FlangeBottom','LensScrewLengthTBD')]:
   for i,xx in enumerate(xs):
    shank=cyl(side+family+'Shank'+str(i),'M2ShankDiameterTBD/2',length,X(xx),Y(y),z)
    head=cyl(side+family+'Head'+str(i),'M2HeadDiameterTBD/2','M2HeadHeightTBD',X(xx),Y(y),'('+z+')-M2HeadHeightTBD')
    screw=union(side+family+'Screw'+str(i),[shank,head],fasteners);screw.Label=side+' '+family+' M2 screw envelope - engagement check required';screws.append(screw)
  # Socket reserve is behind the modeled rear connector only, not an insertion sweep.
  hb=componentDoc.ConnectorReference.Shape.cleaned().BoundBox
  reserve=box(side+'MatingConnectorReserveTBD',str(hb.XLength+1)+' mm',str(hb.YLength+1)+' mm','ExtraConnectorRearReserveTBD',X(str(hb.XMin-.5)+' mm'),Y(str(hb.YMin-.5)+' mm'),'DisplayFront+'+str(hb.ZMin)+' mm-ExtraConnectorRearReserveTBD',reserves)
  # Actual board outline supplies the solder zone. It excludes deliberate contact lands.
  lower=min([f for f in componentDoc.PCBReference.Shape.Faces if type(f.Surface).__name__=='Plane' and f.Area>100],key=lambda f:f.CenterOfMass.z)
  planar=doc.addObject('Part::Feature',side+'PCBRearSourceOutline');construction.addObject(planar)
  shape=lower.copy();shape.translate(App.Vector(0,0,-lower.CenterOfMass.z));planar.Shape=shape
  # Face locations carry the imported normalization transform. Preserve it
  # when adding the assembly offset instead of replacing it with the LCD axis.
  location=planar.Placement.Base
  ex(planar,'Placement.Base.x','('+cx+')+'+str(location.x)+' mm');ex(planar,'Placement.Base.y','('+cy+')+'+str(location.y)+' mm');ex(planar,'Placement.Base.z','PCBBack')
  solder=doc.addObject('Part::Extrusion',side+'RawSolderZone');construction.addObject(solder);solder.Base=planar;solder.DirMode='Custom';solder.Dir=App.Vector(0,0,-1);ex(solder,'LengthFwd','SolderHeightTBD');solder.Solid=True
  exclusions=[]
  for i,(xx,yy,rr) in enumerate([('HoleLeftX','SourceHoleY','NeckClampDiameter/2'),('HoleRightX','SourceHoleY','NeckClampDiameter/2'),('-BackPadX','BackPadY','BackPadDiameter/2'),('BackPadX','BackPadY','BackPadDiameter/2')]):
   exclusions.append(cyl(side+'ContactException'+str(i),'('+rr+')+ContactKeepoutMarginTBD','SolderHeightTBD+0.2 mm',X(xx),Y(yy),'PCBBack-SolderHeightTBD-0.1 mm'))
  exclusions.append(box(side+'HeaderSolderException',str(hb.XLength+1)+' mm',str(hb.YLength+1)+' mm','SolderHeightTBD+0.2 mm',X(str(hb.XMin-.5)+' mm'),Y(str(hb.YMin-.5)+' mm'),'PCBBack-SolderHeightTBD-0.1 mm'))
  solderZone=cut(side+'SolderKeepoutTBD',solder,union(side+'SolderExceptions',exclusions),reserves)
  solderZone.Label=side+' 1 mm solder keepout except four verified-needed contact pads/header'
  return {'ring':ring,'cradle':cradle,'posts':posts,'pilots':pilots,'pocket':pocket,'relief':relief,'contacts':contacts,'screws':screws,'solder':solderZone,'connector':reserve}
 return {'p':p,'aliases':aliases,'ex':ex,'box':box,'cyl':cyl,'union':union,'cut':cut,'rounded':rounded,'system':add_system,'construction':construction,'parts':fabricated,'fasteners':fasteners,'reserves':reserves}

def appearance(o,color,alpha=0):
 o.ViewObject.ShapeColor=color;o.ViewObject.Transparency=alpha;o.ViewObject.LineColor=(.24,.27,.25)
 m=o.ViewObject.ShapeAppearance[0];m.SpecularColor=(0,0,0);m.Shininess=.1;o.ViewObject.ShapeAppearance=[m]

S=setup(assembly)
systems=[]
for side,x in [('Left','Parameters.LCDLeftX'),('Right','Parameters.LCDRightX')]:
 system=S['system'](side,x,'Parameters.LCDY');systems.append(system)
 link=assembly.getObject(side+'CandidateLCD');link.setExpression('Placement.Base.z','LCDMountParameters.DisplayFront')
 link.Label=side+' LCD working reference - user reports match; numerical dimensions not measured'
 for oldName in [side+'LensRetainerTBD',side+'CandidateLCDMatingReserveTBD']:assembly.getObject(oldName).Visibility=False
supportBlank=S['union']('PanelWithLCDPosts',[assembly.FrontHousingRounded]+[p for sys in systems for p in sys['posts']])
tools=S['union']('LCDPanelMachiningTools',[o for sys in systems for o in sys['pilots']+[sys['pocket'],sys['relief']]])
front=S['cut']('LCDIntegratedFrontHousing',supportBlank,tools,S['parts']);front.Label='Front housing with blind rear pilots, PCB standoffs, lens and connector pockets'
assembly.FrontHousingRounded.Visibility=False
assembly.RearTrayRounded.Visibility=False
appearance(front,(.86,.81,.70))
for sys in systems:appearance(sys['ring'],(.77,.75,.65));appearance(sys['cradle'],(.48,.59,.53))
assembly.recompute()
for o in S['construction'].Group:o.Visibility=False
for o in S['fasteners'].Group:appearance(o,(.45,.45,.43));o.Visibility=False
for o in S['reserves'].Group:o.Visibility=False
for sys in systems:sys['ring'].Visibility=True;sys['cradle'].Visibility=True
front.Visibility=True
for name in ['LCDLeftBoardTBD','LCDRightBoardTBD','LeftActiveDisplayProxyTBD','RightActiveDisplayProxyTBD']:assembly.getObject(name).Visibility=False
assembly.recompute()

# Independent coupon: same construction functions and parameter values, no need
# to open the full enclosure to adjust its dimensions.
fit=App.newDocument('MyFirstQubit_LCD_Fit_Test');fit.Label='LCD fit coupon 64 x 68 - dimensional/fastener trial only'
F=setup(fit,True)
single=F['system']('Test','CouponCenterX','CouponCenterY')
plate=F['rounded']('CouponPanelBlank','CouponWidth','CouponDepth','CouponCornerRadius','PanelThickness','0 mm','0 mm','PanelBottom')
aperture=F['cyl']('CouponAperture','ApertureDiameterTBD/2','PanelThickness+0.2 mm','CouponCenterX','CouponCenterY','PanelBottom-0.1 mm')
pocket=F['cyl']('CouponLensPocket','LensPocketDiameterTBD/2','PanelThickness-LensRecess+0.1 mm','CouponCenterX','CouponCenterY','PanelBottom-0.1 mm')
blank=F['union']('CouponWithPosts',[plate]+single['posts'])
coupon=F['cut']('DimensionedFitCoupon',blank,F['union']('CouponPocketTools',[aperture,pocket,single['pocket'],single['relief']]+single['pilots']),F['parts'])
coupon.Label='64 x 68 mm panel coupon - LCD axis (32,36), 5 mm panel'
fit.recompute();fit.saveAs(str(fitFile)) # FreeCAD requires a saved owner for external links.
module=fit.addObject('App::Link','TestLCDWorkingReference');module.setLink(component);F['ex'](module,'Placement.Base.x','CouponCenterX');F['ex'](module,'Placement.Base.y','CouponCenterY');F['ex'](module,'Placement.Base.z','DisplayFront')
lens=F['cyl']('TestPolycarbonateLens','LensDiameterTBD/2','LensThicknessTBD','CouponCenterX','CouponCenterY','LensBottom',F['parts']);lens.Label='Separate clear polycarbonate lens - do not print in opaque filament';appearance(lens,(.72,.85,.88),78)
fit.recompute()
for o in F['construction'].Group:o.Visibility=False
for o in F['reserves'].Group:o.Visibility=False
for o in F['fasteners'].Group:appearance(o,(.45,.45,.43));o.Visibility=True
appearance(coupon,(.86,.81,.70));appearance(single['ring'],(.77,.75,.65));appearance(single['cradle'],(.48,.59,.53))
coupon.Visibility=True;single['ring'].Visibility=True;single['cradle'].Visibility=True

# Native printable parts layout, excludes purchased LCD, lens and screws.
printGroup=fit.addObject('App::DocumentObjectGroup','PrintLayout')
printGroup.Label='Print-only layout - 3 links, no electronics/lens/fasteners'
for obj,name,x in [(coupon,'PrintPanel',0),(single['ring'],'PrintLensRing',72),(single['cradle'],'PrintCradle',137)]:
 link=fit.addObject('App::Link',name);printGroup.addObject(link);link.setLink(obj)
 b=obj.Shape.BoundBox
 if obj==coupon:link.Placement=App.Placement(App.Vector(0,68,5),App.Rotation(App.Vector(1,0,0),180))
 else:link.Placement=App.Placement(App.Vector(x-b.XMin,-b.YMin,-b.ZMin),App.Rotation())
 link.Visibility=False
fit.recompute()

# Save before validation so later review can inspect any reported failures.
assembly.recompute();fit.recompute();assembly.save();fit.saveAs(str(fitFile))

def validate():
 report={'source_status':'User reports physical modules match imported model. No exact caliper measurements supplied; all source dimensions are working-model values.',
  'protected_sha256':hashes,'invalid':[],'collisions':[],'keepout_conflicts':[],'clearances':[],
  'lens_gap_target_mm':2,'previous_lens_gap_mm':5.5,'coupon_mm':[64,68,5],
  'screw_note':'M2 envelopes only, no threads. Pilot engagement is deliberate material interference, not collision-free screw threads.'}
 omitted={'LCDLeftBoardTBD','LCDRightBoardTBD','LeftActiveDisplayProxyTBD','RightActiveDisplayProxyTBD','LeftLensRetainerTBD','RightLensRetainerTBD'}
 others=list(assembly.DiscoveryControls.Group)+[o for o in assembly.ElectronicsPlaceholders.Group if o.Name not in omitted]+[o for o in assembly.ProtectedDisplays.Group if o.Name not in omitted]+[assembly.RearTrayRounded,front]
 printed=[sys[key] for sys in systems for key in ['ring','cradle']]
 parts=others+printed
 for doc,objs in [(assembly,parts),(fit,[coupon,single['ring'],single['cradle'],lens])]:
  for o in objs:
   if o.Shape.isNull() or not o.Shape.isValid() or len(o.Shape.Solids)!=1:report['invalid'].append([doc.Name,o.Name,len(o.Shape.Solids)])
  report.setdefault('recompute_errors',[]).extend([[doc.Name,o.Name,str(o.State)] for o in doc.Objects if 'Invalid' in o.State])
 for i,a in enumerate(parts):
  for b in parts[i+1:]:
   vol=a.Shape.common(b.Shape).Volume
   if vol>.001:report['collisions'].append([a.Name,b.Name,vol])
 for side,sys in zip(['Left','Right'],systems):
  link=assembly.getObject(side+'CandidateLCD')
  for part in [componentDoc.PCBReference,componentDoc.ConnectorReference,componentDoc.DisplayBodyReference]:
   sh=part.Shape.copy();sh.transformShape(link.Placement.toMatrix())
   for other in parts:
    vol=sh.common(other.Shape).Volume;dist=sh.distToShape(other.Shape)[0]
    if vol>.001:report['collisions'].append([side+part.Name,other.Name,vol])
    if other in [front,sys['ring'],sys['cradle'],assembly.getObject(side+'PolycarbonateLensTBD'),assembly.RearTrayRounded]:report['clearances'].append([side,part.Name,other.Name,dist,vol])
  for keepout in [sys['solder'],sys['connector']]:
   for other in parts:
    vol=keepout.Shape.common(other.Shape).Volume
    if vol>.001:report['keepout_conflicts'].append([keepout.Name,other.Name,vol])
 report['part_counts']={'assembly_printed_mounts':len(printed),'fit_printed_parts':3}
 mm=lambda name:assembly.LCDMountParameters.get(name).Value
 report['screw_stack_mm']={
  'PCB_engagement':mm('BracketBottom')+mm('PCBScrewLengthTBD')-mm('PCBFront'),
  'PCB_tip_to_pilot_end':mm('PCBFront')+mm('PCBPilotDepthTBD')-(mm('BracketBottom')+mm('PCBScrewLengthTBD')),
  'lens_engagement':mm('FlangeBottom')+mm('LensScrewLengthTBD')-mm('PanelBottom'),
  'pilot_roof_minimum':mm('PanelTop')-(mm('PCBFront')+mm('PCBPilotDepthTBD'))}
 report['driver_access']={'assumed_diameter_mm':mm('DriverDiameterTBD'),'reach_mm':mm('DriverReachTBD'),'PCB_driver_conflicts':[],'lens_driver_blockers_with_LCD_installed':[]}
 for side,sys in zip(['Left','Right'],systems):
  for family in ['PCB','Lens']:
   for i in range(2):
    head=assembly.getObject(side+family+'Head'+str(i));h=head.Shape.cleaned().BoundBox
    tool=Part.makeCylinder(mm('DriverDiameterTBD')/2,mm('DriverReachTBD'),App.Vector(head.Placement.Base.x,head.Placement.Base.y,h.ZMin-mm('DriverReachTBD')))
    for other in parts:
     if tool.common(other.Shape).Volume>.001:
      key='PCB_driver_conflicts' if family=='PCB' else 'lens_driver_blockers_with_LCD_installed'
      report['driver_access'][key].append([side+family+str(i),other.Name])
 return report
report=validate();(cad/'LCD-mechanical-validation.json').write_text(json.dumps(report,indent=2))
print('VALIDATION',json.dumps({k:v for k,v in report.items() if k not in ['protected_sha256','clearances']},indent=2))

# Disposable review document: exploded and cut section copies never alter designs.
def shot(doc,path,q):
 App.setActiveDocument(doc.Name);v=Gui.activeDocument().activeView();v.setCameraType('Orthographic');Gui.Selection.clearSelection();v.getCameraNode().orientation.setValue(coin.SbRotation(*q));Gui.updateGui();v.fitAll();Gui.updateGui();v.saveImage(str(path),1600,1250,'White')
ax=(.3647051996310009,.2798481423331213,.11591689595929514,.8804762392171493)
shot(assembly,cad/'LCD-mechanical-inside.png',(.8804762392171493,-.11591689595929514,.2798481423331213,-.3647051996310009))
review=App.newDocument('LCD_Integration_Exploded_Review')
for i,(obj,z,col) in enumerate([(coupon,20,(.86,.81,.70)),(lens,10,(.72,.85,.88)),(single['ring'],0,(.77,.75,.65)),(module,-10,(.21,.37,.30)),(single['cradle'],-20,(.48,.59,.53))]):
 o=review.addObject('Part::Feature','Exploded'+str(i));o.Label=obj.Label;s=obj.Shape.copy();s.translate(App.Vector(-32,-36,z));o.Shape=s;appearance(o,col,55 if obj==lens else 0)
review.recompute();shot(review,cad/'LCD-mount-exploded.png',ax);App.closeDocument(review.Name)
review=App.newDocument('LCD_Integration_Section_Review')
# Plane through display and header center, one half removed; no clips to originals.
half=Part.makeBox(80,100,80,App.Vector(32,-10,-40))
for i,(obj,col) in enumerate([(coupon,(.86,.81,.70)),(lens,(.72,.85,.88)),(single['ring'],(.70,.68,.57)),(module,(.21,.37,.30)),(single['cradle'],(.48,.59,.53))]):
 s=obj.Shape.common(half)
 if not s.isNull():o=review.addObject('Part::Feature','Section'+str(i));o.Label=obj.Label;o.Shape=s;appearance(o,col,25 if obj==lens else 0)
review.recompute();shot(review,cad/'LCD-mount-section.png',(.5,-.5,-.5,.5));App.closeDocument(review.Name)
# Fit assembly and the separate three-part print layout.
shot(fit,cad/'LCD-fit-test-assembled.png',ax)
for obj in [coupon,lens,module,single['ring'],single['cradle']]+list(F['fasteners'].Group):obj.Visibility=False
for obj in printGroup.Group:obj.Visibility=True
shot(fit,cad/'LCD-fit-test-print-layout.png',ax)
for obj in printGroup.Group:obj.Visibility=False
for obj in [coupon,lens,module,single['ring'],single['cradle']]+list(F['fasteners'].Group):obj.Visibility=True
settings=App.ParamGet('User parameter:BaseApp/Preferences/Document');old=settings.GetInt('CountBackupFiles',1);settings.SetInt('CountBackupFiles',0)
try:fit.save();assembly.save()
finally:settings.SetInt('CountBackupFiles',old)
for path,h in hashes.items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==h,'Prior reference changed: '+path
App.setActiveDocument(assembly.Name);Gui.activeDocument().activeView().fitAll();Gui.updateGui()
print('SAVED',assemblyFile,fitFile)
