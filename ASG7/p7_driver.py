import subprocess
import json
import collections
import random
import sys

def solve(*args):
    """Run clingo with the provided argument list and return the parsed JSON result."""
    
    CLINGO = "./clingo"
    path = "gringo level-core.lp level-style.lp level-sim.lp level-shortcuts.lp -c width=7 ^ | reify ^ | clingo - meta.lp metaD.lp metaO.lp metaS.lp ^ --parallel-mode=4 --outf=2 > example_noshortcut.json"
    clingo = subprocess.Popen(
        # Have to comment for some reason, fixes the bufsize must be an integer error
        #[CLINGO, "--outf=2"] + list(args),
        path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell = True)
    out, err = clingo.communicate()
    if err:
        print err
        
    return parse_json_result(out)

def parse_json_result(out):
    """Parse the provided JSON text and extract a dict
    representing the predicates described in the first solver result."""
    with open('example_noshortcut.json') as f:
        result = json.load(f)

    #result = json.loads(out)
    
    assert len(result['Call']) > 0
    assert len(result['Call'][0]['Witnesses']) > 0
    
    witness = result['Call'][0]['Witnesses'][0]['Value']
    
    class identitydefaultdict(collections.defaultdict):
        def __missing__(self, key):
            return key
    
    preds = collections.defaultdict(set)
    env = identitydefaultdict()
    
    for atom in witness:
        if '(' in atom:
            left = atom.index('(')
            functor = atom[:left]
            arg_string = atom[left:]
            try:
                preds[functor].add( eval(arg_string, env) )
            except TypeError:
                pass # at least we tried...
            
        else:
            preds[atom] = True
    
    return dict(preds)

def solve_randomly(*args):
    """Like solve() but uses a random sign heuristic with a random seed."""
    args = list(args) + ["--sign-def=3","--seed="+str(random.randint(0,1<<30))]
    return solve(*args) 

def render_ascii_dungeon(design):
    """Given a dict of predicates, return an ASCII-art depiction of the a dungeon."""
    
    sprite = dict(design['sprite'])
    param = dict(design['param'])
    width = param['width']
    glyph = dict(space='.', wall='W', altar='a', gem='g', trap='_')
    block = ''.join([''.join([glyph[sprite.get((r,c),'space')]+' ' for c in range(width)])+'\n' for r in range(width)])
    return block

def render_ascii_touch(design, target):
    """Given a dict of predicates, return an ASCII-art depiction where the player explored
    while in the `target` state."""
    
    touch = collections.defaultdict(lambda: '-')
    for cell, state in design['touch']:
        if state == target:
            touch[cell] = str(target)
    param = dict(design['param'])
    width = param['width']
    block = ''.join([''.join([str(touch[r,c])+' ' for c in range(width)])+'\n' for r in range(width)])
    return block

def side_by_side(*blocks):
    """Horizontally merge two ASCII-art pictures."""
    
    lines = []
    for tup in zip(*map(lambda b: b.split('\n'), blocks)):
        lines.append(' '.join(tup))
    return '\n'.join(lines)

map = solve()
render_map0 = render_ascii_dungeon(map)
#render_map1 = render_ascii_touch(map, 1)
#render_map2 = render_ascii_touch(map, 2)
#render_map3 = render_ascii_touch(map, 3)
print render_map0
#print render_map1
#print render_map2
#print render_map3