## Define mini-templates for each portion of the doco.

<%!
  import re

  def docstring(d, all_items):
      string = d.docstring
      for name in all_items.keys():
          string = string.replace('`%s`' % name, '[`%s`](#%s)' % (name, github_anchor(name)))
      return string
      
          
  truncate = lambda text, n: text if len(text) < n else text[:n-5] + ' ... ' 
  ql = lambda doc: '(' if doc.__class__.__name__ != 'Variable' else ' '
  qr = lambda doc: ')' if doc.__class__.__name__ != 'Variable' else ' '
    
  def github_anchor(val):
    val = val.strip().lower()
    val = re.sub(r'[^\w\- ]+', ' ', val)
    val = re.sub(r'\s+', '-', val)
    val = val.rstrip('-')
    return val
  
  def function_spec(doc, spec=True, bind=None):
      if doc.__class__.__name__ != 'Function':
          return ' '
      if spec == True:
          spec = []
          for p in doc.params():
              if '=' in p:
                  if p.split('=', 1)[1] == 'None':
                      # optional parameter
                      p, _ = p.split('=')
                  else:
                      # parameter with default value
                      pass
                  p = '[%s]' % p
              elif p.startswith('*'):
                  # variable length parameter
                  p = p[1:] + '...'
              
              spec.append(p)
      if bind.__class__.__name__ != 'TopLevel':
          # exclude first `self` parameter
          spec = spec[1:]
      return ', '.join(spec) if spec else ' '
      
  def get_binding_name(bind):
      if bind.__class__.__name__ == 'TopLevel':
          return '_'
      return bind
%>

<%def name="bind_part(bind_and_spec)">${get_binding_name(bind_and_spec[0])}.</%def>
<%def name="spec_part(doc, bind_and_spec)">${function_spec(doc, bind_and_spec[1], bind_and_spec[0])}</%def>

<%def name="signature(doc, bind_and_spec)" filter="trim">
## __`_.castTo(`__*`v, type`*__`)`__
__`${bind_part(bind_and_spec)}${doc.mi_method.name}${ql(doc)}`__*`${spec_part(doc, bind_and_spec)}`*__`${qr(doc)}`__
</%def>


<%def name="function(doc)" filter="trim">
${"###"} ${doc.mi_method.name}
    % for bind, spec in doc.mi_method.combination:
- ${signature(doc, (bind, spec))}
    % endfor

${docstring(doc, all_items)}
- - - - - - - - - - - -
</%def>


## Start the output logic for an entire module.

Modules
-------
| Module | Description |
|--------|-------------|
% for module in modules:
| [${module['name']}](#${github_anchor("Module " + module['name'])}) | --- |
% endfor

% for module in modules:

Module *${module['name']}*
=======${'=' * len(module['name'])}
${docstring(module['module'], all_items)}

Contents
--------
| Signature | Description |
|-----------|-------------|
    % for doc in module['items']:
| [${signature(doc, doc.mi_method.combination[0])}](#${github_anchor(doc.mi_method.name)}) | ${truncate(doc.mi_method.shortdesc, 50)} |
    % endfor

Defines
-------
    % for item in module['items']:
${function(item)}

    % endfor

% endfor
