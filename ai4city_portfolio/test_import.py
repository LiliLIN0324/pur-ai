import traceback
with open('import_test.log','w',encoding='utf-8') as f:
    try:
        import torch
        f.write('torch OK: ' + getattr(torch, '__version__', 'unknown') + '\n')
    except Exception as e:
        f.write('torch ERR: ' + repr(e) + '\n')
        traceback.print_exc(file=f)
    try:
        import visual_tools
        f.write('visual_tools OK\n')
    except Exception as e:
        f.write('visual_tools ERR: ' + repr(e) + '\n')
        traceback.print_exc(file=f)
print('wrote import_test.log')
