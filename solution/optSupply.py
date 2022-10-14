#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import json
import copy
from pyomo.environ import value
#from pyomo.core.kernel.numvalue import value
# replace path below with a path to aaa_dgalPy
#sys.path.append("/Users/alexbrodsky/Documents/OneDrive - George Mason University - O365 Production/aaa_python_code")
sys.path.append("./solution")
import ams

sys.path.append("./lib")
import dgalPy as dgal

#import aaa_dgalPy.lib.dgalPy as dgal


dgal.startDebug()
#f = open("exampleSCinput.json", "r")
#input = json.loads(f.read())
f = open("example_input_output/combined_supply_in_var.json","r")
varInput = json.loads(f.read())

def constraints(o):
    # f = open("example_input_output/combined_supply_out.json","r")
    # o = json.loads(f.read())

    rootService = o["rootService"]
    services = o["services"]
    outFlow = services[rootService]["outFlow"]

    # mat1Amount = value(sum([
    #     outFlow[m]["qty"]
    #     for m in outFlow
    #     if outFlow[m]["item"] == "mat1"
    # ]))
    # mat1Amount
    # mat1Constraint = mat1Amount >= 1000
    # mat1Constraint
    #
    # mat2Amount = value(sum([
    #     outFlow[m]["qty"]
    #     for m in outFlow
    #     if outFlow[m]["item"] == "mat2"
    # ]))
    # mat2Amount
    # mat2Constraint = mat2Amount >= 2000

    # mat1Constraint = (value(outFlow["mat1_sup1"]["qty"] + outFlow["mat1_sup2"]["qty"]) >= 1000)
    # mat2Constraint = (value(outFlow["mat2_sup1"]["qty"] + outFlow["mat2_sup2"]["qty"]) >= 2000)

    sub = {}
    for sup in o["services"]:
        #print(sup)
        if o["services"][sup]["type"]!="composite":
            sub.update({sup: o["services"][sup]})
    sub
    nonNegativityConstraint = dgal.all([
        sub["sup1"]["outFlow"]["mat1_sup1"]["qty"]>=0,
        sub["sup2"]["outFlow"]["mat1_sup2"]["qty"]>=0,
        sub["sup1"]["outFlow"]["mat2_sup1"]["qty"]>=0,
        sub["sup2"]["outFlow"]["mat2_sup2"]["qty"]>=0
    ])

    mat1Constraint = ((sub["sup1"]["outFlow"]["mat1_sup1"]["qty"] + sub["sup2"]["outFlow"]["mat1_sup2"]["qty"]) >= 1000)
    mat2Constraint = ((sub["sup1"]["outFlow"]["mat2_sup1"]["qty"] + sub["sup2"]["outFlow"]["mat2_sup2"]["qty"]) >= 2000)


    additional = dgal.all([mat1Constraint, mat2Constraint, nonNegativityConstraint])
    #additional
    #o["constraints"]
    return (dgal.all([ o["constraints"], additional]))

optAnswer = dgal.min({
    "model": ams.combinedSupply,
    "input": varInput,
    "obj": lambda o: o["cost"],
    "constraints": constraints,
    "options": {"problemType": "mip", "solver":"glpk","debug": True}
})
optOutput = ams.combinedSupply(optAnswer["solution"])
dgal.debug("optOutput",optOutput)
dgal.debug("constraints", optOutput["constraints"])

output = {
#    "input":input,
#    "varInput":varInput,
    "optAnswer": optAnswer,
    "optOutput": optOutput
}
f = open("answers/outOptSupply.json","w")
f.write(json.dumps(output))
