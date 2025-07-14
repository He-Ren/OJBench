import setuptools

def load_requirements(path):
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setuptools.setup(
    name="ojbench",
    version="0.0.3",
    author="He_Ren",
    author_email="1994068337@qq.com",
    description="A competition-level code benchmark for evaluating LLMs",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/He-Ren/OJBench",
    packages=setuptools.find_packages(),
    install_requires=load_requirements("requirements.txt"),
)
