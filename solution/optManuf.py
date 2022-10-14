#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import json
import copy
# replace path below with a path to aaa_dgalPy
# sys.path.append("/Users/alexbrodsky/Documents/OneDrive - George Mason University - O365 Production/aaa_python_code")
#
# import aaa_dgalPy.lib.dgalPy as dgal
# import ams

sys.path.append("./solution")
import ams

sys.path.append("./lib")
import dgalPy as dgal

dgal.startDebug()
#f = open("exampleSCinput.json", "r")
#input = json.loads(f.read())
f = open("example_input_output/combined_manuf_in_var.json","r")
varInput = json.loads(f.read())

def constraints(o):
# replace the Boolean expression below to express that
# The total amount of product1 (prod1_manuf2) is at least 1000,
# and of product2 (prod2_manuf2) is at least 2000
    rootService = o["rootService"]
    services = o["services"]
    outFlow = services[rootService]["outFlow"]

    prod1Constraint = (outFlow["prod1_manuf2"]["qty"] >= 1000)
    prod2Constraint = (outFlow["prod2_manuf2"]["qty"] >= 2000)

    nonNegativityConstraint = dgal.all([
        outFlow["prod1_manuf2"]["qty"] >= 0,
        outFlow["prod2_manuf2"]["qty"] >= 0
    ])

    # sub = {}
    # for sup in o["services"]:
    #     #print(sup)
    #     if o["services"][sup]["type"]!="composite":
    #         sub.update({sup: o["services"][sup]})
    # sub
    # nonNegativityConstraint = dgal.all([
    #     sub["sup1"]["outFlow"]["mat1_sup1"]["qty"]>=0,
    #     sub["sup2"]["outFlow"]["mat1_sup2"]["qty"]>=0,
    #     sub["sup1"]["outFlow"]["mat2_sup1"]["qty"]>=0,
    #     sub["sup2"]["outFlow"]["mat2_sup2"]["qty"]>=0
    # ])

    # mat1Constraint = ((sub["sup1"]["outFlow"]["mat1_sup1"]["qty"] + sub["sup2"]["outFlow"]["mat1_sup2"]["qty"]) >= 1000)
    # mat2Constraint = ((sub["sup1"]["outFlow"]["mat2_sup1"]["qty"] + sub["sup2"]["outFlow"]["mat2_sup2"]["qty"]) >= 2000)


    additional = dgal.all([prod1Constraint, prod2Constraint, nonNegativityConstraint])
    #additional
    #o["constraints"]
    return (dgal.all([ o["constraints"], additional]))

optAnswer = dgal.min({
    "model": ams.combinedManuf,
    "input": varInput,
    "obj": lambda o: o["cost"],
    "constraints": constraints,
    "options": {"problemType": "mip", "solver":"glpk","debug": True}
})
optOutput = ams.combinedManuf(optAnswer["solution"])
dgal.debug("optOutput",optOutput)
dgal.debug("constraints", optOutput["constraints"])

output = {
#    "input":input,
#    "varInput":varInput,
    "optAnswer": optAnswer,
    "optOutput": optOutput
}
f = open("answers/outOptManuf.json","w")
#f.write(str(output))
f.write(json.dumps(output))
#f.write(str(output))

#print("\n dgal opt output \n", optAnswer)
#print(json.dumps(optAnswer))
