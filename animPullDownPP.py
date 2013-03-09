#pull down anim from root (or higher) node, which gets set to 000

import maya.cmds as cmds
import maya.OpenMaya as om
import math
from functools import partial
import maya.mel as mel

#set up UI to enter master controls into list, then enter IK, COG into list
def animPullDownUI():
    if cmds.window("animPullDownWin",exists=True):
        cmds.deleteUI("animPullDownWin", window=True)
        cmds.windowPref("animPullDownWin", remove=True)

    cmds.window("animPullDownWin", w=460, h=300)
    cmds.rowColumnLayout("mainRC", nc=2)

    #----------get frame range

    #master controls layout
    cmds.frameLayout("zeroFrameLO", l="Zeroed Controls", w=230, h=150)
    cmds.columnLayout("zeroColumnLO", w=230, h=150)
    cmds.text("select master control items to zero out")
    cmds.button("zeroButton", l="add scene objs", w=230, c= partial(getControl, "masterTSL"))

    cmds.rowColumnLayout("zeroRCLO", nc=2, w=230)
    cmds.button("clearZeroButton", l="clear selected", w=115, c= partial(clearList, "masterTSL"))
    cmds.button("moveZeroButton", l="move up", w=115, en=False, c= partial(moveUp, "masterTSL"))
    cmds.setParent("zeroColumnLO")
    cmds.separator(h=10)
    cmds.textScrollList("masterTSL", nr=8, ams=True, bgc=(.2, .2, .2))
    #create button to remove selected
    #create method to move around list (reorder)


    #ik items layout
    cmds.setParent("mainRC")
    cmds.frameLayout("IKFrameLO", l = "worldSpace Controls", w=230, h=200)
    cmds.columnLayout("IKColumnLO", w=230, h=150)
    cmds.text("select world space controls")
    cmds.button("IKButton", l="add scene objs", w=230, c= partial(getControl, "IKTSL"))

    cmds.rowColumnLayout("IKRCLO", nc=2, w=230)
    cmds.button("clearIKButton", l="clear selected", w=115, c= partial(clearList, "IKTSL"))
    cmds.button("moveIKButton", l="move up", w=115, en=False, c= partial(moveUp, "masterTSL"))
    cmds.setParent("IKColumnLO")
    cmds.separator(h=10)
    cmds.textScrollList("IKTSL", nr=8, ams=True, bgc=(.2, .2, .2))

    #doIt button layout
    cmds.setParent("animPullDownWin")
    cmds.columnLayout("doItLayout", w=150, h=100)
    cmds.button("doItButton", l="zero out master controls!", w=150, bgc = (0,.5,0), c=pullDownAnim)

    #showWindow
    cmds.showWindow("animPullDownWin")

def moveUp(layout, *args):
     """moves the selected text scroll item up one position"""
     pass
#     #get the selection
#     sel = cmds.textScrollList(layout, q=True, sii=True)
#     for item in sel:
#         if item > 1:
#

def clearList(layout, *args):
    """clears the list of textFields"""
    #get selected items
    sel = cmds.textScrollList(layout, q=True, sii=True)
    #remove selected items
    for item in sel:
        cmds.textScrollList(layout, e=True, rii=True)

def getControl(layout, *args):
    """gets the selected objs and puts them into the assoc. layout"""
    selList = cmds.ls(sl=True, type="transform", l=True)
    if selList:
        cmds.textScrollList(layout, e=True, a=selList)

def getLocalValues(obj, *args):
    """use the matrix to get world space vals, convert to trans and rots"""
    #get values
    #add as key in dict
    obj_values = []

    obj_wRot = cmds.xform(obj, q=True, ws=True, ro=True)
    obj_wTrans = cmds.xform(obj, q=True, ws=True, t=True)

    for tval in obj_wTrans:
        obj_values.append(tval)
    for rval in obj_wRot:
        obj_values.append(rval)

    return obj_values
    #return (tx, ty, tz, rx, ry, rz)


def pullDownAnim(*args):
    #get master controls
    masters = []
    rawKeys = []
    keyList = []
    worldCtrls = []
    currentTime = mel.eval("currentTime-q;")
    allControls = []
    
    #get list of master ctrls
    mChildren = cmds.textScrollList("masterTSL", q=True, ai=True)
    for thisM in mChildren:
        masters.append(thisM)
        allControls.append(thisM)
        
    #get list of world space objects
    wChildren = cmds.textScrollList("IKTSL", q=True, ai=True)
    for thisIK in wChildren:
        worldCtrls.append(thisIK)
        allControls.append(thisIK)
#------------------get keys from secondary controls also. .  . 
    #get full list of keys (keyList)
    for each in allControls:
        #get list of keys for each master
        keys = cmds.keyframe(each, q=True)
        #add keys to rawKeys
        if keys:
            for thisKey in keys:
                rawKeys.append(thisKey)
        #make list from set of list
        keySet = set(rawKeys)
        for skey in keySet:
            keyList.append(skey)
          
    #if no keys, then just add the current time value
    if not rawKeys:
        keyList.append(currentTime)
    
    keyList.sort()
    print keyList

#-------------
    localVals = {}

#for each control, grab the values at that key and store them in a dict, "control":[(vals), (vals)], list of values are at key indices
    for wCtrl in worldCtrls:
        localList = []
        #store these in a dict (obj:(tx, ty, tz, rx, ry, rz))
        for key in keyList:
            mel.eval("currentTime %s;"%key)
            theseVals = getLocalValues(wCtrl)
            localList.append(theseVals)
        localVals[wCtrl] = localList
    print localVals
    
#zero out the master controls
    for key in range(len(keyList)):
        mel.eval("currentTime %s;"%keyList[key])
        for mCtrl in masters:  #should I use setkey?
            cmds.xform(mCtrl, ws=True, t = (0, 0, 0))
            cmds.xform(mCtrl, ws=True, ro = (0, 0, 0))
            cmds.setKeyframe(mCtrl, ott="step", t=keyList[key])
            
        #THEN setKey each control's values to the values in the dict
        for wCtrl in worldCtrls:
            #--------if attr is locked skip it
            cmds.xform(wCtrl, ws=True, t=(localVals[wCtrl][key][0], localVals[wCtrl][key][1], localVals[wCtrl][key][2]))
            cmds.xform(wCtrl, ws=True, ro=(localVals[wCtrl][key][3], localVals[wCtrl][key][4], localVals[wCtrl][key][5]))
            cmds.setKeyframe(wCtrl, ott="step", t=keyList[key])

def animPullDown():
    animPullDownUI()
    
animPullDown()