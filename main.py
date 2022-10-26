
import yaml
import os
from yaml.loader import SafeLoader

def kustomization_yaml_creater(resource, data):
    print("resource:", resource)
    if (os.path.exists("./output/kustomization.yaml")):
        print("kustomization.yaml existed")
        kustomization_bak = {}
        with open("./output/kustomization.yaml", "r") as sf:
            kustomization = yaml.load(sf, Loader=SafeLoader)
            print(kustomization)
            kustomization_bak = kustomization
            kustomization_bak["resources"].append(resource + ".yaml")
            if (resource == "deployment"):
                image_dic = {"name": "", "newTag": ""}
                image_str = data["image"]
                image_dic["name"] = image_str.split(":", 1)[0]
                image_dic["newTag"] = image_str.split(":", 1)[1]
                kustomization_bak["images"].append(image_dic)
        with open("./output/kustomization.yaml", "w") as df:
            df.write(yaml.dump(kustomization_bak))
    else:
        print("kustomization.yaml creating!!!")
        with open("demo/kustomization.yaml", "r") as sf:
            kustomization = yaml.load(sf, Loader=SafeLoader)
            kustomization["resources"] = []
            kustomization["namespace"] = data["project"]
            kustomization["images"] = []
            #kustomization["resources"].append(resource + ".yaml")

            with open("./output/kustomization.yaml", "w") as df:
                df.write(yaml.dump(kustomization))
    print("finish creating kustomization.yaml")

def namespace_yaml_creater(data):
    print("namespace.yaml creating!!!")
    with open("demo/namespace.yaml", "r") as sf:
        namespace = yaml.load(sf, Loader=SafeLoader)
        namespace["metadata"]["labels"]["name"] = data["namespace"]
        namespace["metadata"]["name"] = data["namespace"]
        with open("./output/namespace.yaml", "w") as f:
            f.write(yaml.dump(namespace))
    kustomization_yaml_creater("namespace", data)
    print("finish creating namespace.yaml")

def ingress_yaml_creater(data):
    print("ingress.yaml creating!!!")
    with open("demo/ingress.yaml", "r") as sf:
        ingress = yaml.load(sf, Loader=SafeLoader)
        ingress["metadata"]["annotations"]["kubernetes.io/ingress.class"] = data["ingress-controller"]
        ingress["metadata"]["name"] = data["project"] + "-ingress"
        ingress["metadata"]["namespace"] = data["project"]
        ingress["metadata"]["annotations"]["cert-manager.io/cluster-issuer"] = data["cluster-issuer"]
        ingress["spec"]["tls"][0]["hosts"][0] = data["domain"]
        ingress["spec"]["tls"][0]["secretName"] = data["project"] + "-tls"
        ingress["spec"]["rules"][0]["host"] = data["domain"]
        ingress["spec"]["rules"][0]["http"]["paths"][0]["backend"]["serviceName"] = data["project"] + "-service"
        with open("./output/ingress.yaml", "w") as f:
            f.write(yaml.dump(ingress))
    kustomization_yaml_creater("ingress", data)
    print("finish creating ingress.yaml")

def service_yaml_creater(data):
    print("service.yaml creating!!!")
    with open("demo/service.yaml", "r") as sf:
        service = yaml.load(sf, Loader=SafeLoader)
        service["metadata"]["name"] = data["project"] + "-service"
        service["metadata"]["namespace"] = data["project"]
        service["spec"]["ports"][0]["targetPort"] = data["container-port"]
        service["spec"]["selector"]["app"] = data["project"]
        with open("./output/service.yaml", "w") as df:
            df.write(yaml.dump(service))
    kustomization_yaml_creater("service", data)
    print("finish creating service.yaml")

def secret_yaml_creater(data, env):
    print("secret.yaml creating!!!")
    with open("demo/secret.yaml", "r") as sf:
        secret = yaml.load(sf, Loader=SafeLoader)
        secret["metadata"]["name"] = data["project"] + "-secret"
        secret["metadata"]["namespace"] = data["project"]
        secret["spec"]["name"] = data["project"] + "-secret"
        lens = len(env)
        key = 0
        secret["spec"]["keysMap"] = {}
        for key in env:
            secret_dic = {"key": "", "path": ""}
            secret["spec"]["keysMap"][key] = secret_dic
            secret["spec"]["keysMap"][key]["key"] = key
            secret["spec"]["keysMap"][key]["path"] = data["secret"]["path"]
        with open("./output/secret.yaml", "w") as df:
            df.write(yaml.dump(secret))
    kustomization_yaml_creater("secret", data)
    print("finish creating secret.yaml")

def pvc_yaml_creater(data):
    print("pvc.yaml creating!!!")

    print("finish creating pvc.yaml")


def deployment_yaml_creater(data):
    print("deployment.yaml creating!!!")
    with open("demo/deployment.yaml", "r") as sf:
        deployment = yaml.load(sf, Loader=SafeLoader)
        deployment["metadata"]["name"] = data["project"] + "-deployment"
        deployment["metadata"]["namespace"] = data["project"]
        deployment["spec"]["replicas"] = data["replicas"]
        deployment["spec"]["selector"]["matchLabels"]["app"] = data["project"]
        deployment["spec"]["template"]["metadata"]["labels"]["app"] = data["project"]
        deployment["spec"]["template"]["spec"]["containers"][0]["name"] = data["project"]
        deployment["spec"]["template"]["spec"]["containers"][0]["image"] = data["image"]
        deployment["spec"]["template"]["spec"]["containers"][0]["resources"]["requests"]["cpu"] = \
        data["resources"]["requests"]["cpu"]
        deployment["spec"]["template"]["spec"]["containers"][0]["resources"]["requests"]["memory"] = \
        data["resources"]["requests"]["memory"]
        deployment["spec"]["template"]["spec"]["containers"][0]["resources"]["limits"]["cpu"] = \
            data["resources"]["limits"]["cpu"]
        deployment["spec"]["template"]["spec"]["containers"][0]["resources"]["limits"]["memory"] = \
            data["resources"]["limits"]["memory"]
        deployment["spec"]["template"]["spec"]["containers"][0]["readinessProbe"] = data["healthy"]["readinessProbe"]
        deployment["spec"]["template"]["spec"]["containers"][0]["livenessProbe"] = data["healthy"]["livenessProbe"]
        if (data["env"] is not None):
            deployment["spec"]["template"]["spec"]["containers"][0]["env"] = data["env"]
            lens = len(data["env"])
            str_addr = 0
            env_list = []
            for env in data["env"]:
                env_dic = {"secretKeyRef": {"name": "", "key": ""}}
                deployment["spec"]["template"]["spec"]["containers"][0]["env"][str_addr]["valueFrom"] = env_dic
                key = deployment["spec"]["template"]["spec"]["containers"][0]["env"][str_addr]["name"].lower()
                deployment["spec"]["template"]["spec"]["containers"][0]["env"][str_addr]["valueFrom"]["secretKeyRef"]["key"] = key
                deployment["spec"]["template"]["spec"]["containers"][0]["env"][str_addr]["valueFrom"]["secretKeyRef"][
                    "name"] = data["project"] + "-secret"
                env_list.append(key)
                str_addr += 1
            secret_yaml_creater(data, env_list)

        else:
            print("env is null")

        if (data["pvc"] is not None):
            print("pvc is not null")

            if ("volumeMounts" in deployment["spec"]["template"]["spec"]["containers"][0]):
                print("volumeMounts is exist")
            else:
                print("volumeMounts is not found")
                deployment["spec"]["template"]["spec"]["containers"][0]["volumeMounts"] = []
                lens = len(data["pvc"])
                print(lens)
                args = 0
                for pvc_str in data["pvc"]:
                    mount_dic = {"name": "", "mountPath": ""}
                    deployment["spec"]["template"]["spec"]["containers"][0]["volumeMounts"].append(mount_dic)
                    print(deployment["spec"]["template"]["spec"]["containers"][0]["volumeMounts"])
                    deployment["spec"]["template"]["spec"]["containers"][0]["volumeMounts"][args]["name"] = "container_mountpath" + str(args)
                    deployment["spec"]["template"]["spec"]["containers"][0]["volumeMounts"][args]["mountPath"] = pvc_str["mountpath"]
                    volume_dic = {"name": "", "persistentVolumeClaim": {"claimName": ""}}
                    if ("volumes" in deployment["spec"]["template"]["spec"]):
                        print("volumes is exsit")
                        deployment["spec"]["template"]["spec"]["volumes"].append(volume_dic)
                        deployment["spec"]["template"]["spec"]["volumes"][args]["name"] = \
                        deployment["spec"]["template"]["spec"]["containers"][0]["volumeMounts"][args]["name"]
                        deployment["spec"]["template"]["spec"]["volumes"][args]["persistentVolumeClaim"][
                            "claimName"] = "pvc-" + str(args)
                    else:
                        print("volumes is not exsit")
                        deployment["spec"]["template"]["spec"]["volumes"] = []
                        deployment["spec"]["template"]["spec"]["volumes"].append(volume_dic)
                        deployment["spec"]["template"]["spec"]["volumes"][args]["name"] = deployment["spec"]["template"]["spec"]["containers"][0]["volumeMounts"][args]["name"]
                        deployment["spec"]["template"]["spec"]["volumes"][args]["persistentVolumeClaim"]["claimName"] = "pvc-" + str(args)

                    args += 1
        else:
            print("pvc is null")
        with open("./output/deployment.yaml", "w") as df:
            df.write(yaml.dump(deployment))
    kustomization_yaml_creater("deployment", data)
    print("finish creating deployment.yaml")

def source_reader(source_file):
    if (os.path.exists("./output") == True):
        if (os.remove("./output/kustomization.yaml")):
            print("clean workdir")
    else:
        os.makedirs("./output")
    with open(source_file) as f:
        data = yaml.load(f, Loader=SafeLoader)
        kustomization_yaml_creater("", data)
        namespace_yaml_creater(data)
        ingress_yaml_creater(data)
        service_yaml_creater(data)
        deployment_yaml_creater(data)

if __name__ == '__main__':
    print("welcome k8s yaml creater")
    source_reader("source.yaml")