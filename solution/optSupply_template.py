#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import json
import copy
# replace path below with a path to aaa_dgalPy
sys.path.append("/Users/alexbrodsky/Documents/OneDrive - George Mason University - O365 Production/aaa_python_code")

import aaa_dgalPy.lib.dgalPy as dgal
import ams

dgal.startDebug()
#f = open("exampleSCinput.json", "r")
#input = json.loads(f.read())
f = open("example_input_output/combined_supply_in_var.json","r")
varInput = json.loads(f.read())

def constraints(o):
#   replace the  Boolean expression below, in terms of model output o, to say
#   that the total amount of mat1 (mat1_sup1 + mat1_sup2) is at least 1000 &
#   the total amount of mat2 is 2000.
    additional = True
    return (dgal.all([ o["constraints"], additional])

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
f = open("answers/outOptSupply.json","w")ion
f.write(json.dumps(output))
