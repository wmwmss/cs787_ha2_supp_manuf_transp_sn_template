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
f = open("example_input_output/combined_manuf_in_var.json","r")
varInput = json.loads(f.read())

def constraints(o):
# replace the Boolean expression below to express that
# The total amount of product1 (prod1_manuf2) is at least 1000,
# and of product2 (prod2_manuf2) is at least 2000

    additional = True
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
