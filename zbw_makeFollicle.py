########################
#file: zbw_makeFollicle.py
#author: zeth willie
#contact: zeth@catbuks.com, www.williework.blogspot.com
#date modified: 
#
#notes: select a vertex on a polysurface and type name and create follicle
########################

#create a follicle on the specified uv location
import maya.cmds as cmds
import maya.mel as mel

widgets = {}

#here create a UI that will just pass info into the main func. So you can call function if you want with args or use the UI
def follicleUI(*args):
    if cmds.window("folWin", exists=True):
        cmds.deleteUI("folWin")
        
    widgets["win"] = cmds.window("folWin", t="zbw_makeFollicle", w=300, h=100)
    widgets["mainCLO"] = cmds.columnLayout()
    
    widgets["text"] = cmds.text("Select one or two verts (2 will get avg position) and run")
    widgets["nameTFG"] = cmds.textFieldGrp(l="FollicleName:", cal=([1, "left"],[2,"left"]), cw=([1,100],[2,200]))
    cmds.separator(h=10)
    widgets["button"] = cmds.button(w=300, h=50, bgc=(0.6,.8,.6), l="Add follicle", c=getUV)

    cmds.showWindow(widgets["win"])
    cmds.window(widgets["win"], e=True, w=300, h=100)
#-------could also select edit point????
#-------multiple selection and average uv position? Orrrr option to create multiple UV's, one on each vertex
#-------grab an edge and convert to 2 verts and get average. . .
#-------have option for distributed (select 2 verts and number of follicles, spread that num between the two uv positions)

def getUV(*args):
    """takes a selection of one or two verts and returns one UV position. If just the surface is selected, it will return UV vals of (.5, .5)"""
    #get vertex
    sel = cmds.ls(sl=True)
    #------filter for vertices (or cvs?)
    vertices = cmds.filterExpand(sm=(31), fp=True, ex=True)
    print "verts = %s"%vertices
    if len(vertices)>2:
        cmds.warning("You've selected more than two verts. Two is the max number I can take")
        
    uvs = []

    if vertices:
        #here deal with option to use one or average uv values of two selections (shouldn't be more than two)? 
        for vert in vertices:
            #convert vertex to uvs
            thisUV = cmds.polyListComponentConversion(vert, fv=True, tuv=True)[0]
            uvs.append(thisUV)
        else:
            cmds.warning("You haven't selected any verts! Select one or two to place a follicle")

        print "uvs = %s"%uvs
        #convert vertices to uvs and get their value
        if uvs:
            uvList = []
            for uv in uvs:
                #grab first (cuz verts can be multiple uv's)
                thisUV = cmds.ls(uv)[0]
                #convert the uv index to u and v values
                uvVal = cmds.polyEditUV(uv, q=True)
                uvList.append(uvVal)
            
            U = []
            V = []
            sizeUV = len(uvList)
            #print uvList
            for uv in uvList:
                U.append(uv[0])
                V.append(uv[1])
            #print "U = %s"%U
            #print "V = %s"%V
            #DO THE AVERAGING HERE
            x = 0
            y = 0 
            for a in U:
                x = x + a
            for b in V:
                y = y + b
            
            u = x/sizeUV
            v = y/sizeUV
            
            uvVal = [u,v]
            print uvVal
            
            cmds.select(vertices)
            print "THESE ARE THE OUTPUTS"
            print "vertex is: %s"%vertices[0]
            shapeName = vertices[0].rpartition(".vtx")[0]
            meshName = cmds.listRelatives(shapeName, p=True)[0]
            print meshName
            folName = cmds.textFieldGrp(widgets["nameTFG"], q=True, tx=True)
            print folName
            uValue = uvVal[0]
            print uValue
            vValue = uvVal[1]
            print vValue
            follicle(meshName, folName, uValue, vValue)
            
        else:
            pass

def follicle(surface="none", folName="none", u=0.5, v=0.5, *args): 
#------------do a bit more checking here to make sure the shapes, numbers etc work out
#------------i.e. make sure the name of the follicle isn't already taken before trying to create the new one
    # print "surface is: %s"%surface
    # print "folName is: %s"%folName
    if surface=="none":
        #decide if surface is polymesh or nurbsSurface
        #TO-DO----------------make this more generic so I can use it elsewhere
        surfaceXform = cmds.ls(sl=True, dag=True, type="transform")[0]
        surfaceShape = cmds.listRelatives(surfaceXform, shapes=True)[0]
    else:
        surfaceXform = surface
        surfaceShape = cmds.listRelatives(surfaceXform, shapes=True)[0]

    if folName == "none":
        folShapeName = "myFollicleShape"
        folXformName = "myFollicle"
    else:
        folShapeName = "%sShape"%folName
        folXformName = folName

	#create the follicle
    folShape = cmds.createNode("follicle", n=folShapeName)
    folXform = cmds.listRelatives(folShape, p=True, type="transform")[0]
    cmds.rename(folXform, folXformName)

    #connect up the follicle!
    #connect the matrix of the surface to the matrix of the follicle
    cmds.connectAttr("%s.worldMatrix[0]"%surfaceShape, "%s.inputWorldMatrix"%folShape)

    #check for surface type, poly or nurbs and connect the matrix into the follicle
    if (cmds.nodeType(surfaceShape)=="nurbsSurface"):
        cmds.connectAttr("%s.local"%surfaceShape, "%s.inputSurface"%folShape)
    elif (cmds.nodeType(surfaceShape)=="mesh"):
        cmds.connectAttr("%s.outMesh"%surfaceShape, "%s.inputMesh"%folShape)
    else:
        cmds.warning("not the right kind of selection. Need a poly or nurbs surface")

    #connect the transl, rots from shape to transform of follicle
    cmds.connectAttr("%s.outTranslate"%folShape, "%s.translate"%folXform)
    cmds.connectAttr("%s.outRotate"%folShape, "%s.rotate"%folXform)

    cmds.setAttr("%s.parameterU"%folShape, u)
    cmds.setAttr("%s.parameterV"%folShape, v)

    cmds.setAttr("%s.translate"%folXform, l=True)
    cmds.setAttr("%s.rotate"%folXform, l=True)


def makeFollicle():
    follicleUI()