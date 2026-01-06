# Copyright (C) 2012 Robert Lanfear and Brett Calcott
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details. You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# PartitionFinder also includes the PhyML program, the RAxML program, and the
# PyParsing library, all of which are protected by their own licenses and
# conditions, using PartitionFinder implies that you agree with those licences
# and conditions as well.

import logtools
import os
from config import the_config

log = logtools.get_logger()
from util import PartitionFinderError


_MODEL_PARAM_TOTAL_CACHE = None
_MODEL_PARAM_TOTAL_CACHE_SOURCE_ID = None


def _get_model_param_total_cache():
    global _MODEL_PARAM_TOTAL_CACHE
    global _MODEL_PARAM_TOTAL_CACHE_SOURCE_ID

    df = getattr(the_config, "available_models", None)
    if df is None:
        _MODEL_PARAM_TOTAL_CACHE = {}
        _MODEL_PARAM_TOTAL_CACHE_SOURCE_ID = None
        return _MODEL_PARAM_TOTAL_CACHE

    source_id = id(df)
    if _MODEL_PARAM_TOTAL_CACHE is not None and _MODEL_PARAM_TOTAL_CACHE_SOURCE_ID == source_id:
        return _MODEL_PARAM_TOTAL_CACHE

    # Build a fast lookup: model name -> total param count.
    cache = {}
    try:
        # New fast path: list-of-dicts loaded from models.csv.
        if isinstance(df, list):
            for row in df:
                if not isinstance(row, dict):
                    continue
                name = row.get('name')
                if not name:
                    continue
                m = row.get('matrix_params') or 0
                b = row.get('basefreq_params') or 0
                r = row.get('ratevar_params') or 0
                cache[str(name)] = int(m) + int(b) + int(r)
        else:
            # Backwards compatible: DataFrame-like.
            subset = df[["name", "matrix_params", "basefreq_params", "ratevar_params"]]
            for name, m, b, r in subset.itertuples(index=False, name=None):
                try:
                    cache[name] = int(m) + int(b) + int(r)
                except Exception:
                    # If types are unexpected, fall back to Python's + behavior.
                    cache[name] = m + b + r
    except Exception:
        # Defensive fallback.
        cache = {}

    _MODEL_PARAM_TOTAL_CACHE = cache
    _MODEL_PARAM_TOTAL_CACHE_SOURCE_ID = source_id
    return _MODEL_PARAM_TOTAL_CACHE

def get_num_params(modelstring):
    """
    Input a model string like HKY+I+G or LG+G+F, and get the number of
    parameters
    """

    # Handle bytes in Python 3
    if isinstance(modelstring, bytes):
        modelstring = modelstring.decode('utf-8')

    cache = _get_model_param_total_cache()
    try:
        total = cache[modelstring]
    except KeyError:
        raise PartitionFinderError(f"Unknown model: {modelstring}")

    log.debug("Model: %s Params: %d" % (modelstring, total))

    return total

def get_raxml_protein_modelstring(modelstring):
    """Start with a model like this: LG+I+G+F, return a model in raxml format like this:
    LGF. This is only used for printing out RAxML partition files
    NB. In RAxML you can't specify different rate hetero parameters in each protein model
    you have to choose either ALL +G or ALL +I+G. PartitionFinder allows you to mix and 
    match here, but if you're going to use RAxML downstream, you will need to be smarter
    and run two analyses - one with just +I+G models, and one with +G models. 

    So really all we do is add an F/X to the model name if it used +F.
    """
    
    # Handle bytes object
    if isinstance(modelstring, bytes):
        modelstring = modelstring.decode('utf-8')

    elements = modelstring.split("+")
    model_name = elements[0]
    extras = elements[1:]

    raxmlstring = model_name
    if "F" in extras:
        raxmlstring = ''.join([raxmlstring, "F"])
    elif "X" in extras:
        raxmlstring = ''.join([raxmlstring, "X"])    

    return raxmlstring


def get_raxml_morphology_modelstring(modelstring):
    """Start with a model like this: MULTI+G+A, return a model in raxml format like this:
    MULTI. This is only used for printing out RAxML partition files
    """
    
    # Handle bytes object
    if isinstance(modelstring, bytes):
        modelstring = modelstring.decode('utf-8')

    elements = modelstring.split("+")
    model_name = elements[0]

    if model_name == "MULTISTATE":
        return("MULTI")
    elif model_name == "BINARY":
        return("BIN")

def get_mrbayes_modeltext_DNA(modelstring, i):
    """Start with a model like this: GTR+I+G, or LG+I+G, return some text that can be 
    used to run a model like it in MrBayes"""

    # Handle bytes in Python 3
    if isinstance(modelstring, bytes):
        modelstring = modelstring.decode('utf-8')
    
    elements = modelstring.split("+")
    model_name = elements[0]
    extras = elements[1:]

    if model_name in ["GTR", "SYM"]: nst = 6
    elif model_name in ["HKY", "K80"]: nst = 2
    elif model_name in ["F81", "JC"]: nst = 1
    else: nst = 6 # default for models not implemented in MrBayes

    if model_name in ["SYM", "K80", "JC"]:
        equal_rates = "prset applyto=(%d) statefreqpr=fixed(equal);\n" % i
    else:
        equal_rates = ""

    if "I" not in extras and "G" not in extras:
        rate_var = ""
    elif "I" in extras and "G" not in extras:
        rate_var = " rates=propinv"
    elif "I" not in extras and "G" in extras:
        rate_var = " rates=gamma"
    elif "I" in extras and "G" in extras:
        rate_var = " rates=invgamma"

    text = "\tlset applyto=(%d) nst=%d%s;\n%s" %(i, nst, rate_var, equal_rates)

    return text

def get_mrbayes_modeltext_protein(modelstring, i):
    
    # Handle bytes object
    if isinstance(modelstring, bytes):
        modelstring = modelstring.decode('utf-8')

    elements = modelstring.split("+")
    model_name = elements[0]
    extras = elements[1:]

    if model_name in ['JTT', 'DAYHOFF', 'MTREV', 'MTMAM', 'WAG', 'RTREV', 
                      'CPREV', 'VT', 'BLOSUM', 'GTR']:
        model = model_name.lower()
    else:
        model = 'wag'

    if model == 'jtt': model = 'jones' # because MrBayes uses 'jones'

    if "I" not in extras and "G" not in extras:
        rate_var = ""
    elif "I" in extras and "G" not in extras:
        rate_var = " rates=propinv"
    elif "I" not in extras and "G" in extras:
        rate_var = " rates=gamma"
    elif "I" in extras and "G" in extras:
        rate_var = " rates=invgamma"

    if rate_var != "":
        line_1 = "\tlset applyto=(%d)%s;\n" %(i, rate_var)
    else:
        line_1 = ""

    line_2 = "\tprset applyto=(%d) aamodelpr=fixed(%s);\n" %(i, model)

    text = ''.join([line_1, line_2])

    return text
