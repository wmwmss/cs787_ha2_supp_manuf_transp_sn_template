import copy
import json
#import importlib.util
#from importlib import util
import sys
# sys.path.append("../aaa_dgalPy")
sys.path.append("./lib")
# sys.path.append("/Users/alexbrodsky/Documents/OneDrive - George Mason University - O365 Production/aaa_python_code/aaa_dgalPy")
import dgalPy as dgal

sys.path.append("..")

# the following is a useful Boolean function returning True if all qty's in newFlow are non-negative
# and greater than or equal to the lower bounds (lb) in flow (inFlow or outFlow)
# replace below with correct implementation if you'd like to use it in analytic models below
# def flowBoundConstraint(flow,newFlow):
#     nonNegativityConstraint = dgal.all([True for mat in newFlow if newFlow[mat]['qty']>=0])
#
#     try:
#         lbs = [mat['lb'] for mat in flow]
#     except:
#         lbConstraint = dgal.all([True for mat in newFlow if newFlow[mat]['qty']>=flow[mat]['lb']])
#     else:
#         lbConstraint = dgal.all([True for mat in newFlow if newFlow[mat]['qty']>=flow[mat]['qty']])
#
#     return (nonNegativityConstraint and lbConstraint)

def flowBoundConstraint(flowBounds,flow):
    c = dgal.all([ [flow[f]["qty"] >= 0, flow[f]["qty"] >= flowBounds[f]["lb"]] for f in flow])
    return(c)
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
    '''# test
    supInput = {
      "type": "supplier",
      "inFlow": {},
      "outFlow": {
        "mat1_sup1": {
          "qty": 2000,
          "lb": 0,
          "ppu": 5,
          "item": "mat1"
        },
        "mat2_sup1": {
          "qty": 1500,
          "lb": 0,
          "ppu": 4,
          "item": "mat2"
        }
      }
    }
    # end of test'''

    type = supInput["type"]
    inFlow = supInput["inFlow"]
    outFlow = supInput["outFlow"]

    ppu = [outFlow[mat]['ppu'] for mat in outFlow]
    qty = [outFlow[mat]['qty'] for mat in outFlow]

# replace below with correct computation
    cost = sum([ppu[i] * qty[i] for i in range(len(qty))])

    newOutFlow = {mat:{"qty": outFlow[mat]["qty"], "item": outFlow[mat]["item"]} for mat in outFlow}

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
    '''# test
    manufInput = {
      "type": "manufacturer",
      "inFlow": {
        "mat1_manuf1": {
          "lb": 0,
          "item": "mat1"
        },
        "mat2_manuf1": {
          "lb": 0,
          "item": "mat2"
        }
      },
      "outFlow": {
        "part1_manuf12": {
          "qty": 300,
          "lb": 0,
          "ppu": 1,
          "item": "part1"
        },
        "part2_manuf12": {
          "qty": 500,
          "lb": 0,
          "ppu": 2,
          "item": "part2"
        }
      },
      "qtyInPer1out": {
        "part1_manuf12": {
          "mat1_manuf1": 2,
          "mat2_manuf1": 1
        },
        "part2_manuf12": {
          "mat2_manuf1": 3
        }
      }
    }
    # end of test'''

    type = manufInput["type"]
    inFlow = manufInput["inFlow"]
    outFlow = manufInput["outFlow"]
    qtyInPer1out = manufInput["qtyInPer1out"]

    ppu = [outFlow[mat]['ppu'] for mat in outFlow]
    qty = [outFlow[mat]['qty'] for mat in outFlow]

    inQty = {mat:sum([outFlow[part]['qty']*qtyInPer1out[part][mat] for part in outFlow if mat in qtyInPer1out[part]]) for mat in inFlow}
    inQty
# replace below with correct computation
    cost = sum([ppu[i] * qty[i] for i in range(len(qty))])
    #cost
    newInFlow = {mat:{"qty": inQty[mat], "item": inFlow[mat]["item"]} for mat in inFlow}
    #newInFlow
    newOutFlow = {mat:{"qty": outFlow[mat]["qty"], "item": outFlow[mat]["item"]} for mat in outFlow}
    #newOutFlow

    inFlowConstraints = flowBoundConstraint(inFlow,newInFlow)
    outFlowConstraints = flowBoundConstraint(outFlow,newOutFlow)
    constraints = dgal.all([ inFlowConstraints, outFlowConstraints])
    #constraints

    return { "type": type,
             "cost": cost,
             "constraints": constraints,
             "inFlow": newInFlow,
             "outFlow": newOutFlow
    }
# end of manufMetrics
#--------------------------------------------------
def transportMetrics(transportInput, shared):
    '''# test
    transportInput = {
      "type": "transport",
      "inFlow": {
        "mat1_sup1": {
          "lb": 0,
          "item": "mat1"
        },
        "mat2_sup1": {
          "lb": 0,
          "item": "mat2"
        },
        "mat1_sup2": {
          "lb": 0,
          "item": "mat1"
        },
        "mat2_sup2": {
          "lb": 0,
          "item": "mat2"
        }
      },
      "outFlow": {
        "mat1_manuf1": {
          "lb": 0,
          "item": "mat1"
        },
        "mat2_manuf1": {
          "lb": 0,
          "item": "mat2"
        }
      },
      "pplbFromTo": {
        "Fairfax": {
          "NYC": 0.5
        },
        "LA": {
          "NYC": 2.5
        }
      },
      "orders": [
        {
          "in": "mat1_sup1",
          "out": "mat1_manuf1",
          "sender": "sup1",
          "recipient": "manuf1",
          "qty": 600
        },
        {
          "in": "mat2_sup1",
          "out": "mat2_manuf1",
          "sender": "sup1",
          "recipient": "manuf1",
          "qty": 700
        },
        {
          "in": "mat1_sup2",
          "out": "mat1_manuf1",
          "sender": "sup2",
          "recipient": "manuf1",
          "qty": 400
        },
        {
          "in": "mat2_sup2",
          "out": "mat2_manuf1",
          "sender": "sup2",
          "recipient": "manuf1",
          "qty": 600
        }
      ]
    }

    shared = {
      "busEntities": {
        "sup1": {
          "loc": "Fairfax"
        },
        "sup2": {
          "loc": "LA"
        },
        "transp1": {
          "loc": "Seattle"
        },
        "transp2": {
          "loc": "Baltimore"
        },
        "manuf1": {
          "loc": "NYC"
        },
        "manuf2": {
          "loc": "NYC"
        }
      },
      "items": {
        "mat1": {
          "weight": 1
        },
        "mat2": {
          "weight": 2
        },
        "part1": {
          "weight": 7
        },
        "part2": {
          "weight": 6
        },
        "prod1": {
          "weight": 8
        },
        "prod2": {
          "weight": 9
        }
      }
    }
    # end of test'''

    type = transportInput["type"]
    inFlow = transportInput["inFlow"]
    outFlow = transportInput["outFlow"]
    pplbFromTo = transportInput["pplbFromTo"]
    orders = transportInput["orders"]
# replace below with correct implementation. Note: it is based on transportation orders
    newInFlow = dict()
    for f in inFlow:
        qty = sum([ o["qty"] for o in orders if o["in"] == f ])
        newInFlow.update({f: {"qty": qty, "item": inFlow[f]["item"]} })

    newOutFlow = dict()
    for f in outFlow:
        qty = sum([ o["qty"] for o in orders if o["out"] == f ])
        newOutFlow.update({f: {"qty": qty, "item": outFlow[f]["item"]} })
# replace below with computation of all source locations
    sourceLocations = set([shared["busEntities"][o["sender"]]["loc"] for o in orders])
    sourceLocations
# replace below with computation of a structure for all source-destination pairs in orders
    destsPerSource = dict()
    for s in sourceLocations:
        dests = set()
        for o in orders:
            senderLoc = shared["busEntities"][o["sender"]]["loc"]
            recipientLoc = shared["busEntities"][o["recipient"]]["loc"]
            if senderLoc == s:
                dests.add(recipientLoc)
        destsPerSource.update({s: list(dests)})
    destsPerSource
# replace below with computation of total weight for every source-destination pair according to orders
    weightCostPerSourceDest = list()
    for s in sourceLocations:
        for d in destsPerSource[s]:
            weight = sum([
                unitWeight * o["qty"]
                for o in orders
                if (shared["busEntities"][o["sender"]]["loc"] == s
                    and shared["busEntities"][o["recipient"]]["loc"])
                for unitWeight in [shared["items"][inFlow[o["in"]]["item"]]["weight"]]
            ])
            cost = pplbFromTo[s][d] * weight
            weightCostPerSourceDest.append({"source": s, "dest": d, "weight": weight, "cost": cost })
    weightCostPerSourceDest
# replace below with transportation cost computation, based on, for each source-destination pair,
# on total weight and price per pound (pplb)
    cost = sum([ sd["cost"] for sd in weightCostPerSourceDest ])
    cost

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
    '''# test
    input = {
      "shared": {
        "busEntities": {
          "sup1": {
            "loc": "Fairfax"
          },
          "sup2": {
            "loc": "LA"
          },
          "transp1": {
            "loc": "Seattle"
          },
          "transp2": {
            "loc": "Baltimore"
          },
          "manuf1": {
            "loc": "NYC"
          },
          "manuf2": {
            "loc": "NYC"
          }
        },
        "items": {
          "mat1": {
            "weight": 1
          },
          "mat2": {
            "weight": 2
          },
          "part1": {
            "weight": 7
          },
          "part2": {
            "weight": 6
          },
          "prod1": {
            "weight": 8
          },
          "prod2": {
            "weight": 9
          }
        }
      },
      "rootService": "combinedSupply",
      "services": {
        "combinedSupply": {
          "type": "composite",
          "inFlow": {},
          "outFlow": {
            "mat1_sup1": {
              "lb": 0,
              "item": "mat1"
            },
            "mat2_sup1": {
              "lb": 0,
              "item": "mat2"
            },
            "mat1_sup2": {
              "lb": 0,
              "item": "mat1"
            },
            "mat2_sup2": {
              "lb": 0,
              "item": "mat2"
            }
          },
          "subServices": [
            "sup1",
            "sup2"
          ]
        },
        "sup1": {
          "type": "supplier",
          "inFlow": {},
          "outFlow": {
            "mat1_sup1": {
              "qty": 2000,
              "lb": 0,
              "ppu": 5,
              "item": "mat1"
            },
            "mat2_sup1": {
              "qty": 1500,
              "lb": 0,
              "ppu": 4,
              "item": "mat2"
            }
          }
        },
        "sup2": {
          "type": "supplier",
          "inFlow": {},
          "outFlow": {
            "mat1_sup2": {
              "qty": 500,
              "lb": 0,
              "ppu": 2,
              "item": "mat1"
            },
            "mat2_sup2": {
              "qty": 1300,
              "lb": 0,
              "ppu": 3,
              "item": "mat2"
            }
          }
        }
      }
    }
    # end of test'''

    rootService = input["rootService"]

    sub = {}
    for sup in input["services"]:
        #print(sup)
        if input["services"][sup]["type"]!="composite":
            sub.update({sup:supplierMetrics(input["services"][sup])})
    sub
    newRootOutFlowDict = {}
    newRootOutFlow = {
        newRootOutFlowDict.update(sub[s]["outFlow"])
        for s in sub
    }
    newRootOutFlowDict

    cost = sum([sub[s]["cost"] for s in sub])
    #cost
    constraints = dgal.all([sub[s]["constraints"] for s in sub])
    #constraints

    subServicesList = [s for s in sub]
    subServicesList

    mainService = {
        rootService:{
            "type": input["services"][rootService]["type"],
            "cost": cost,
            "constraints": constraints,
            "inFlow": {},
            "outFlow": newRootOutFlowDict,
            "subServices": subServicesList
        }
    }
    mainService


    services = {}
    services.update(mainService)
    services.update(sub)
    services

    return {
      "cost": cost,
      "constraints": constraints,
      "rootService": rootService,
      "services": services
      }

def combinedManuf(input):
    '''# test
    input = {
      "shared": {
        "busEntities": {
          "sup1": {
            "loc": "Fairfax"
          },
          "sup2": {
            "loc": "LA"
          },
          "transp1": {
            "loc": "Seattle"
          },
          "transp2": {
            "loc": "Baltimore"
          },
          "manuf1": {
            "loc": "NYC"
          },
          "manuf2": {
            "loc": "NYC"
          }
        },
        "items": {
          "mat1": {
            "weight": 1
          },
          "mat2": {
            "weight": 2
          },
          "part1": {
            "weight": 7
          },
          "part2": {
            "weight": 6
          },
          "prod1": {
            "weight": 8
          },
          "prod2": {
            "weight": 9
          }
        }
      },
      "rootService": "combinedManuf",
      "services": {
        "combinedManuf": {
          "type": "composite",
          "inFlow": {
            "mat1_manuf1": {
              "lb": 0,
              "item": "mat1"
            },
            "mat2_manuf1": {
              "lb": 0,
              "item": "mat2"
            }
          },
          "outFlow": {
            "prod1_manuf2": {
              "lb": 0,
              "item": "prod1"
            },
            "prod2_manuf2": {
              "lb": 0,
              "item": "prod2"
            }
          },
          "subServices": [
            "tier1manuf",
            "tier2manuf"
          ]
        },
        "tier1manuf": {
          "type": "manufacturer",
          "inFlow": {
            "mat1_manuf1": {
              "lb": 0,
              "item": "mat1"
            },
            "mat2_manuf1": {
              "lb": 0,
              "item": "mat2"
            }
          },
          "outFlow": {
            "part1_manuf12": {
              "qty": 300,
              "lb": 0,
              "ppu": 1,
              "item": "part1"
            },
            "part2_manuf12": {
              "qty": 500,
              "lb": 0,
              "ppu": 2,
              "item": "part2"
            }
          },
          "qtyInPer1out": {
            "part1_manuf12": {
              "mat1_manuf1": 2,
              "mat2_manuf1": 1
            },
            "part2_manuf12": {
              "mat2_manuf1": 3
            }
          }
        },
        "tier2manuf": {
          "type": "manufacturer",
          "inFlow": {
            "part1_manuf12": {
              "lb": 0,
              "item": "part1"
            },
            "part2_manuf12": {
              "lb": 0,
              "item": "part2"
            }
          },
          "outFlow": {
            "prod1_manuf2": {
              "qty": 100,
              "lb": 0,
              "ppu": 5,
              "item": "prod1"
            },
            "prod2_manuf2": {
              "qty": 200,
              "lb": 0,
              "ppu": 6,
              "item": "prod2"
            }
          },
          "qtyInPer1out": {
            "prod1_manuf2": {
              "part1_manuf12": 3,
              "part2_manuf12": 1
            },
            "prod2_manuf2": {
              "part2_manuf12": 2
            }
          }
        }
      }
    }
    # end of test data'''

    rootService = input["rootService"]

    sub = {}
    for sup in input["services"]:
        #print(sup)
        if input["services"][sup]["type"]!="composite":
            sub.update({sup:manufMetrics(input["services"][sup])})
    sub
    newRootInFlowDict = {}
    newRootInFlow = {
        newRootInFlowDict.update(sub[s]["inFlow"])
        for s in sub
        if s == "tier1manuf"
    }
    newRootInFlowDict

    newRootOutFlowDict = {}
    newRootOutFlow = {
        newRootOutFlowDict.update(sub[s]["outFlow"])
        for s in sub
        if s == "tier2manuf"
    }
    newRootOutFlowDict

    cost = sum([sub[s]["cost"] for s in sub])
    #cost

    flowConstraints = dgal.all([
        sub[s]["outFlow"].keys() == sub[s1]["inFlow"].keys()
        for s in sub
        for s1 in sub
        if sub[s]["type"] == "manufacturer" and sub[s1]["type"] == "manufacturer"
        and s == "tier1manuf" and s1 == "tier2manuf"
        ])
    flowConstraints

    # quantifyConstraints = dgal.all([
    #     sub[s]["outFlow"][k] == sub[s1]["inFlow"][k]
    #     for s in sub
    #     for s1 in sub
    #     for k in sub[s]["outFlow"]
    #     if sub[s]["type"] == "manufacturer" and sub[s1]["type"] == "manufacturer"
    #     and s == "tier1manuf" and s1 == "tier2manuf"
    #     ])
    quantifyConstraints = dgal.all([
        sub["tier1manuf"]["outFlow"]["part1_manuf12"]["qty"]==sub["tier2manuf"]["inFlow"]["part1_manuf12"]["qty"],
        sub["tier1manuf"]["outFlow"]["part2_manuf12"]["qty"]==sub["tier2manuf"]["inFlow"]["part2_manuf12"]["qty"]
    ])
    quantifyConstraints

    subConstraints = dgal.all([sub[s]["constraints"] for s in sub])
    constraints = dgal.all([flowConstraints, quantifyConstraints, subConstraints])
    constraints

    subServicesList = [s for s in sub]
    subServicesList

    mainService = {
        rootService:{
            "type": input["services"][rootService]["type"],
            "cost": cost,
            "constraints": constraints,
            "inFlow": newRootInFlowDict,
            "outFlow": newRootOutFlowDict,
            "subServices": subServicesList
        }
    }
    mainService


    services = {}
    services.update(mainService)
    services.update(sub)
    services

    return {
      "cost": cost,
      "constraints": constraints,
      "rootService": rootService,
      "services": services
      }

def combinedTransp(input):
    '''# test
    input = {
      "shared": {
        "busEntities": {
          "sup1": {
            "loc": "Fairfax"
          },
          "sup2": {
            "loc": "LA"
          },
          "transp1": {
            "loc": "Seattle"
          },
          "transp2": {
            "loc": "Baltimore"
          },
          "manuf1": {
            "loc": "NYC"
          },
          "manuf2": {
            "loc": "NYC"
          }
        },
        "items": {
          "mat1": {
            "weight": 1
          },
          "mat2": {
            "weight": 2
          },
          "part1": {
            "weight": 7
          },
          "part2": {
            "weight": 6
          },
          "prod1": {
            "weight": 8
          },
          "prod2": {
            "weight": 9
          }
        }
      },
      "rootService": "combinedTransport",
      "services": {
        "combinedTransport": {
          "type": "composite",
          "inFlow": {
            "mat1_sup1": {
              "lb": 0,
              "item": "mat1"
            },
            "mat2_sup1": {
              "lb": 0,
              "item": "mat2"
            },
            "mat1_sup2": {
              "lb": 0,
              "item": "mat1"
            },
            "mat2_sup2": {
              "lb": 0,
              "item": "mat2"
            }
          },
          "outFlow": {
            "mat1_manuf1": {
              "lb": 0,
              "item": "mat1"
            },
            "mat2_manuf1": {
              "lb": 0,
              "item": "mat2"
            }
          },
          "subServices": [
            "transp1",
            "transp2"
          ]
        },
        "transp1": {
          "type": "transport",
          "inFlow": {
            "mat1_sup1": {
              "lb": 0,
              "item": "mat1"
            },
            "mat2_sup1": {
              "lb": 0,
              "item": "mat2"
            },
            "mat1_sup2": {
              "lb": 0,
              "item": "mat1"
            },
            "mat2_sup2": {
              "lb": 0,
              "item": "mat2"
            }
          },
          "outFlow": {
            "mat1_manuf1": {
              "lb": 0,
              "item": "mat1"
            },
            "mat2_manuf1": {
              "lb": 0,
              "item": "mat2"
            }
          },
          "pplbFromTo": {
            "Fairfax": {
              "NYC": 0.5
            },
            "LA": {
              "NYC": 2.5
            }
          },
          "orders": [
            {
              "in": "mat1_sup1",
              "out": "mat1_manuf1",
              "sender": "sup1",
              "recipient": "manuf1",
              "qty": 600
            },
            {
              "in": "mat2_sup1",
              "out": "mat2_manuf1",
              "sender": "sup1",
              "recipient": "manuf1",
              "qty": 700
            },
            {
              "in": "mat1_sup2",
              "out": "mat1_manuf1",
              "sender": "sup2",
              "recipient": "manuf1",
              "qty": 400
            },
            {
              "in": "mat2_sup2",
              "out": "mat2_manuf1",
              "sender": "sup2",
              "recipient": "manuf1",
              "qty": 600
            }
          ]
        },
        "transp2": {
          "type": "transport",
          "inFlow": {
            "mat1_sup1": {
              "lb": 0,
              "item": "mat1"
            },
            "mat2_sup1": {
              "lb": 0,
              "item": "mat2"
            },
            "mat1_sup2": {
              "lb": 0,
              "item": "mat1"
            },
            "mat2_sup2": {
              "lb": 0,
              "item": "mat2"
            }
          },
          "outFlow": {
            "mat1_manuf1": {
              "lb": 0,
              "item": "mat1"
            },
            "mat2_manuf1": {
              "lb": 0,
              "item": "mat2"
            }
          },
          "pplbFromTo": {
            "Fairfax": {
              "NYC": 0.1
            },
            "LA": {
              "NYC": 2
            }
          },
          "orders": [
            {
              "in": "mat1_sup1",
              "out": "mat1_manuf1",
              "sender": "sup1",
              "recipient": "manuf1",
              "qty": 0
            },
            {
              "in": "mat2_sup1",
              "out": "mat2_manuf1",
              "sender": "sup1",
              "recipient": "manuf1",
              "qty": 0
            },
            {
              "in": "mat1_sup2",
              "out": "mat1_manuf1",
              "sender": "sup2",
              "recipient": "manuf1",
              "qty": 0
            },
            {
              "in": "mat2_sup2",
              "out": "mat2_manuf1",
              "sender": "sup2",
              "recipient": "manuf1",
              "qty": 600
            }
          ]
        }
      }
    }
    # end of test'''

    rootService = input["rootService"]
    shared = input["shared"]

    sub = {}
    for sup in input["services"]:
        #print(sup)
        if input["services"][sup]["type"]!="composite":
            sub.update({sup:transportMetrics(input["services"][sup], shared)})
    sub

    # inFlow
    inFlow = sub["transp1"]["inFlow"].copy()
    newRootInFlowDict = sub["transp1"]["inFlow"].copy()
    newRootInFlowDict

    inFlowQty = {
    m: {
        "qty": sum([
            sub[s]["inFlow"][m]["qty"]
            for s in sub
            if sub[s]["type"] == "transport"
            ])
        }
        for m in inFlow
        }
    inFlowQty

    for m in inFlow:
        newRootInFlowDict.update({m:{"qty": inFlowQty[m]["qty"], "item": inFlow[m]["item"]}})
    newRootInFlowDict

    # outFlow
    outFlow = sub["transp1"]["outFlow"].copy()
    newRootOutFlowDict = sub["transp1"]["outFlow"].copy()
    newRootOutFlowDict

    outFlowQty = {
    m: {
        "qty": sum([
            sub[s]["outFlow"][m]["qty"]
            for s in sub
            if sub[s]["type"] == "transport"
            ])
        }
        for m in outFlow
        }
    outFlowQty

    for m in outFlow:
        newRootOutFlowDict.update({m:{"qty": outFlowQty[m]["qty"], "item": outFlow[m]["item"]}})
    newRootOutFlowDict

    cost = sum([sub[s]["cost"] for s in sub])
    #cost
    constraints = dgal.all([sub[s]["constraints"] for s in sub])
    #constraints

    subServicesList = [s for s in sub]
    subServicesList

    mainService = {
        rootService:{
            "type": input["services"][rootService]["type"],
            "cost": cost,
            "constraints": constraints,
            "inFlow": newRootInFlowDict,
            "outFlow": newRootOutFlowDict,
            "subServices": subServicesList
        }
    }
    mainService


    services = {}
    services.update(mainService)
    services.update(sub)
    services

    return {
      "cost": cost,
      "constraints": constraints,
      "rootService": rootService,
      "services": services
      }
