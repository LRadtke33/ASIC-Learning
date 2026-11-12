"""Work around ngspice 44's .lib whitespace parsing without changing model bytes.

Quoted .include paths work, but .lib filenames containing spaces are truncated
by this release. A generated local directory symlink keeps the entire model
tree and its relative includes intact while giving .lib a space-free path.
Default in-course runs do not need or create an alias.
"""
from pathlib import Path
import hashlib,re

def portable_library_paths(deck,folder):
    folder=Path(folder).resolve();folder.mkdir(parents=True,exist_ok=True)
    def replace(match):
        filename=match.group(2)
        if not any(c.isspace() for c in filename):return match.group(0)
        target=(folder/filename).resolve()
        if not target.is_file():raise RuntimeError('Model library file not found: '+str(target))
        if any(c.isspace() for c in target.name):
            raise RuntimeError('ngspice 44 cannot parse whitespace in a .lib filename. Use a model filename without spaces; parent directories may contain spaces.')
        alias=folder/('_course_models_'+hashlib.sha256(str(target.parent).encode()).hexdigest()[:12])
        if alias.is_symlink():
            if alias.resolve()!=target.parent:raise RuntimeError('Unexpected generated model alias: '+str(alias))
        elif alias.exists():raise RuntimeError('Generated model alias name is occupied: '+str(alias))
        else:
            try:alias.symlink_to(target.parent,target_is_directory=True)
            except OSError as error:
                raise RuntimeError('Cannot create a local model-directory alias. Run inside the course tree or choose model/output paths with no whitespace.') from error
        return match.group(1)+'"'+alias.name+'/'+target.name+'"'+match.group(3)
    return re.sub(r'(?im)^(\s*\.lib\s+)"([^"]+)"([^\r\n]*)$',replace,deck)

