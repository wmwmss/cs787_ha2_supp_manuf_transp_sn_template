import copy
import json
import importlib.util
import sys
# sys.path.append("../aaa_dgalPy")
sys.path.append("./lib")
# sys.path.append("/Users/alexbrodsky/Documents/OneDrive - George Mason University - O365 Production/aaa_python_code/aaa_dgalPy")
import dgalPy as dgal

# the following is a useful Boolean function returning True if all qty's in newFlow are non-negative
# and greater than or equal to the lower bounds (lb) in flow (inFlow or outFlow)
# replace below with correct implementation if you'd like to use it in analytic models below
def flowBoundConstraint(flow,newFlow):
    return True

#--------------------------------------------------------------------
#assumptions on input data
#1. root service inFlows and outFlows are disjoint
#2. every inFlow of every subService must have a corresponding root inFlow
#   and/or a corresponding subService outFlow (i.e., an inFlow of a subService can't
#   come from nowhere)
#3. every outFlow of every subService must have a corresponding root outFlow
#   and/or a corresponding subService inFlows (i.e., an outFlow of a subService can't
#  go nowhere)
#4. every root outFlow must have at least one corresponding subService outFlow
#5. every root inFlow must have at least one corresponding subService inFlow
#----------------------------------------------------------------
# you may want to use this template for combinedSupply(input), combindManuf(input)
# and combinedTransp(input) below

def computeMetrics(shared,root,services):
    type = services[root]["type"]
    inFlow = services[root]["inFlow"]
    outFlow = services[root]["outFlow"]

    if type == "supplier":
        return {root: supplierMetrics(services[root])}
    elif type == "manufacturer":
        return {root: manufMetrics(services[root])}
    elif type == "transport":
        return {root: transportMetrics(services[root],shared)}
    else:
        subServices = services[root]["subServices"]
        subServiceMetrics = dgal.merge([computeMetrics(shared,s,services) for s in subServices])
# replace below with correct cost computation
        cost = 1000

# replace below with computation of new InFlow and new OutFlow of the root service
    newInFlow = "TBD"
    newOutFlow = "TBD"
    inFlowConstraints = flowBoundConstraint(inFlow,newInFlow)
    outFlowConstraints = flowBoundConstraint(outFlow,newOutFlow)

# replace below with internal flow constraints
    internalSupplySatisfiesDemand = True

    constraints = dgal.all([ internalSupplySatisfiesDemand,
                            inFlowConstraints,
                            outFlowConstraints,
                            subServiceConstraints
                      ])
    rootMetrics = {
        root : {
            "type": type,
            "cost": cost,
            "constraints": constraints,
            "inFlow": newInFlow,
            "outFlow": newOutFlow,
            "subServices": subServices
        }
    }
    return dgal.merge([ subServiceMetrics , rootMetrics ])

# end of Compute Metrics function
# ------------------------------------------------------------------------------
def supplierMetrics(supInput):
    type = supInput["type"]
    inFlow = supInput["inFlow"]
    outFlow = supInput["outFlow"]

# replace below with correct computation
    cost = 1000

    newOutFlow = "TBD"

    constraints = flowBoundConstraint(outFlow,newOutFlow)
    return {
        "type": type,
        "cost": cost,
        "constraints": constraints,
        "inFlow": dict(),
        "outFlow": newOutFlow
    }
#---------------------------------------------------------------------------------------
# simple manufacturer
# assumption: there is an input flow for every inQtyPer1out

def manufMetrics(manufInput):
    type = manufInput["type"]
    inFlow = manufInput["inFlow"]
    outFlow = manufInput["outFlow"]
    qtyInPer1out = manufInput["qtyInPer1out"]
# replace below with correct computation
    cost = 1000
    newInFlow = "TBD"
    newOutFlow = "TBD"

    inFlowConstraints = flowBoundConstraint(inFlow,newInFlow)
    outFlowConstraints = flowBoundConstraint(outFlow,newOutFlow)
    constraints = dgal.all([ inFlowConstraints, outFlowConstraints])

    return { "type": type,
             "cost": cost,
             "constraints": constraints,
             "inFlow": newInFlow,
             "outFlow": newOutFlow
    }
# end of manufMetrics
#--------------------------------------------------
def transportMetrics(transportInput, shared):
    type = transportInput["type"]
    inFlow = transportInput["inFlow"]
    outFlow = transportInput["outFlow"]
    pplbFromTo = transportInput["pplbFromTo"]
    orders = transportInput["orders"]
# replace below with correct implementation. Note: it is based on transportation orders
    newInFlow = "TBD"
    newOutFlow = "TBD"
# replace below with computation of all source locations
    sourceLocations = "TBD"
# replace below with computation of a structure for all source-destination pairs in orders
    destsPerSource = "TBD"
# replace below with computation of total weight for every source-destination pair according to orders
    weightCostPerSourceDest = "TBD"
# replace below with transportation cost computation, based on, for each source-destination pair,
# on total weight and price per pound (pplb)
    cost = 1000

    inFlowConstraints = flowBoundConstraint(inFlow,newInFlow)
    outFlowConstraints = flowBoundConstraint(outFlow,newOutFlow)
    constraints = dgal.all([inFlowConstraints,outFlowConstraints])
    return { "type": type,
             "cost": cost,
             "constraints": constraints,
             "inFlow": newInFlow,
             "outFlow": newOutFlow
    }
# replace below with correct implementation
def combinedSupply(input):
    return "TBD"
def combinedManuf(input):
    return "TBD"
def combinedTransp(input):
    return "TBD"
