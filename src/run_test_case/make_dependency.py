import os
import sys
import subprocess
import glob
from pathlib import Path


def has_made(project_dir):
    """
    If the project has made before
    """
    for dirpath, dirnames, filenames in os.walk(project_dir):
        if 'pom.xml' in filenames and 'target' in dirnames:
            target = os.path.join(dirpath, 'target')
            if 'dependency' in os.listdir(target):
                return True
    return False


def make_dependency(project_dir):
    '''
    Generate runtime dependencies of a given project
    '''
    MVN_DEPENDENCE_DIR = 'target/dependency'

    deps = []
    if not has_made(project_dir):
        # Run mvn command to generate dependencies
        print("Making dependency for project", project_dir)
        subprocess.run(f"mvn dependency:copy-dependencies -DoutputDirectory={MVN_DEPENDENCE_DIR} -f {project_dir}/pom.xml", shell=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(f"mvn install -DskipTests -f {project_dir}/pom.xml", shell=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # if not os.path.exists(f"{project_dir}/{MVN_DEPENDENCE_DIR}"):

    dep_jars = glob.glob(project_dir + "/**/*.jar", recursive=True)
    deps.extend(dep_jars)
    # for dirpath, dirnames, filenames in os.walk(project_dir):
    #     if MVN_DEPENDENCE_DIR in dirnames:
    #         deps_path = dirpath
    #         deps.extend([str(Path(deps_path) / f) for f in os.listdir(deps_path)])
    deps = list(set(deps))
    return ':'.join(deps)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python make_dependency.py <absolute_target_path>")
        sys.exit()
    make_dependency(sys.argv[1])
