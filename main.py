
import yaml
import os
from yaml.loader import SafeLoader

def kustomization_yaml_creater(resource, data, namespace):
    print("resource:", resource)
    if (os.path.exists("./output/kustomization.yaml")):
        print("kustomization.yaml existed")
        kustomization_bak = {}
        with open("./output/kustomization.yaml", "r") as sf:
            kustomization = yaml.load(sf, Loader=SafeLoader)
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
            kustomization["namespace"] = namespace
            kustomization["images"] = []
            with open("./output/kustomization.yaml", "w") as df:
                df.write(yaml.dump(kustomization))
    print("finish creating kustomization.yaml")

def namespace_yaml_creater(data):
    print("namespace.yaml creating!!!")
    with open("demo/namespace.yaml", "r") as sf:
        namespace = yaml.load(sf, Loader=SafeLoader)
        namespace["metadata"]["labels"]["name"] = data["project"]
        namespace["metadata"]["name"] = data["project"]
        with open("./output/namespace.yaml", "w") as f:
            f.write(yaml.dump(namespace))
    kustomization_yaml_creater("namespace", data, data["project"])
    print("finish creating namespace.yaml")


def service_yaml_creater(data, namespace):
    print("service creating!!!")
    with open("demo/service.yaml", "r") as sf:
        service = yaml.load(sf, Loader=SafeLoader)
        service["metadata"]["name"] = data["name"] + "-service"
        service["metadata"]["namespace"] = namespace
        service["spec"]["ports"][0]["targetPort"] = data["port"]
        service["spec"]["selector"]["app"] = data["name"]
        file_name = "./output/" + data["name"] + "-service.yaml"
        with open(file_name, "w") as df:
            df.write(yaml.dump(service))
        kustomization_yaml_creater(data["name"] + "-service", data, namespace)
        print("finish creating " + file_name)

def network_yaml_creater(data, namespace):
    print("network creating!!!")
    if ( data["network"] == "ingress" ):
        file_name = "output/" + data["name"] + "-ingress.yaml"
        with open("demo/ingress.yaml", "r") as sf:
            ingress = yaml.load(sf, Loader=SafeLoader)
            ingress["metadata"]["annotations"]["kubernetes.io/ingress.class"] = data["ingress-controller"]
            ingress["metadata"]["name"] = data["name"] + "-ingress"
            ingress["metadata"]["namespace"] = namespace
            ingress["metadata"]["annotations"]["cert-manager.io/cluster-issuer"] = data["cluster-issuer"]
            ingress["spec"]["tls"][0]["hosts"][0] = data["domain"]
            ingress["spec"]["tls"][0]["secretName"] = data["name"] + "-tls"
            ingress["spec"]["rules"][0]["host"] = data["domain"]
            ingress["spec"]["rules"][0]["http"]["paths"][0]["backend"]["serviceName"] = data["name"] + "-service"
            ingress["spec"]["rules"][0]["http"]["paths"][0]["path"] = data["path"]
            with open(file_name, "w") as f:
                f.write(yaml.dump(ingress))
        kustomization_yaml_creater(data["name"] + "-ingress", data, namespace)
        print("finish creating " + data["name"] + "-ingress.yaml")
        service_yaml_creater(data, namespace)
    elif ( data["network"] == "loadbalance" ):
        print("loadbalance is still in developing")
    elif (data["network"] == "clusterip"):
        print("clusterip is still in developing")


def secret_yaml_creater(data, env, namespace):
    print("secret.yaml creating!!!")
    with open("demo/secret.yaml", "r") as sf:
        secret = yaml.load(sf, Loader=SafeLoader)
        secret["metadata"]["name"] = data["name"] + "-secret"
        secret["metadata"]["namespace"] = namespace
        secret["spec"]["name"] = data["name"] + "-secret"
        lens = len(env)
        key = 0
        secret["spec"]["keysMap"] = {}
        for key in env:
            secret_dic = {"key": "", "path": ""}
            secret["spec"]["keysMap"][key] = secret_dic
            secret["spec"]["keysMap"][key]["key"] = key
            secret["spec"]["keysMap"][key]["path"] = data["secret_path"]
        file_path = "./output/" + secret["metadata"]["name"] + ".yaml"
        with open(file_path, "w") as df:
            df.write(yaml.dump(secret))
    kustomization_yaml_creater(secret["metadata"]["name"], data, namespace)
    print("finish creating " + secret["metadata"]["name"])

def pvc_yaml_creater(pvc_dic, data, namespace):
    print("pvc.yaml creating!!!")
    with open("demo/pvc.yaml", "r") as sf:
        pvc = yaml.load(sf, Loader=SafeLoader)
        pvc["metadata"]["name"] = pvc_dic["name"]
        pvc["metadata"]["namespace"] = namespace
        pvc["spec"]["accessModes"] = []
        pvc["spec"]["accessModes"].append(pvc_dic["accessModes"])
        pvc["spec"]["resources"]["requests"]["storage"] = pvc_dic["size"]
        pvc["spec"]["storageClassName"] = pvc_dic["storageClassName"]
        file_path = "./output/" + pvc_dic["name"] + ".yaml"
        with open(file_path, "w") as df:
            df.write(yaml.dump(pvc))
        kustomization_yaml_creater(pvc["metadata"]["name"], data, namespace)
    print("finish creating " + pvc["metadata"]["name"])


def deployment_yaml_creater(data, namespace):
    print("deployment.yaml creating!!!")
    with open("demo/deployment.yaml", "r") as sf:
        deployment = yaml.load(sf, Loader=SafeLoader)
        deployment["metadata"]["name"] = data["name"] + "-deployment"
        deployment["metadata"]["namespace"] = namespace
        deployment["spec"]["replicas"] = data["replicas"]
        deployment["spec"]["selector"]["matchLabels"]["app"] = data["name"]
        deployment["spec"]["template"]["metadata"]["labels"]["app"] = data["name"]
        deployment["spec"]["template"]["spec"]["containers"][0]["name"] = data["name"]
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
                env_dic = {"name": "", "valueFrom": {"secretKeyRef": {"name": "", "key": ""}}}
                deployment["spec"]["template"]["spec"]["containers"][0]["env"][str_addr] = env_dic
                deployment["spec"]["template"]["spec"]["containers"][0]["env"][str_addr]["name"] = env
                key = deployment["spec"]["template"]["spec"]["containers"][0]["env"][str_addr]["name"].lower()
                deployment["spec"]["template"]["spec"]["containers"][0]["env"][str_addr]["valueFrom"]["secretKeyRef"]["key"] = key
                deployment["spec"]["template"]["spec"]["containers"][0]["env"][str_addr]["valueFrom"]["secretKeyRef"][
                    "name"] = data["name"] + "-secret"
                env_list.append(key)
                str_addr += 1
            secret_yaml_creater(data, env_list, namespace)

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
                    # print(deployment["spec"]["template"]["spec"]["containers"][0]["volumeMounts"])
                    deployment["spec"]["template"]["spec"]["containers"][0]["volumeMounts"][args]["name"] = "container-mountpath-" + str(args)
                    deployment["spec"]["template"]["spec"]["containers"][0]["volumeMounts"][args]["mountPath"] = pvc_str["mountpath"]
                    volume_dic = {"name": "", "persistentVolumeClaim": {"claimName": ""}}
                    if ("volumes" in deployment["spec"]["template"]["spec"]):
                        # print("volumes is exsit")
                        deployment["spec"]["template"]["spec"]["volumes"].append(volume_dic)
                        deployment["spec"]["template"]["spec"]["volumes"][args]["name"] = \
                        deployment["spec"]["template"]["spec"]["containers"][0]["volumeMounts"][args]["name"]
                        deployment["spec"]["template"]["spec"]["volumes"][args]["persistentVolumeClaim"][
                            "claimName"] = data["name"] + "-pvc-" + str(args)
                    else:
                        # print("volumes is not exsit")
                        deployment["spec"]["template"]["spec"]["volumes"] = []
                        deployment["spec"]["template"]["spec"]["volumes"].append(volume_dic)
                        deployment["spec"]["template"]["spec"]["volumes"][args]["name"] = deployment["spec"]["template"]["spec"]["containers"][0]["volumeMounts"][args]["name"]
                        deployment["spec"]["template"]["spec"]["volumes"][args]["persistentVolumeClaim"]["claimName"] = data["name"] + "-pvc-" + str(args)
                    pvc_dic = {"name": "", "size": "", "accessModes": "", "storageClassName": ""}
                    pvc_dic["name"] = data["name"] + "-pvc-" + str(args)
                    pvc_dic["size"] = pvc_str["size"]
                    pvc_dic["accessModes"] = pvc_str["accessModes"]
                    pvc_dic["storageClassName"] = pvc_str["storageClassName"]
                    pvc_yaml_creater(pvc_dic, data, namespace)
                    args += 1
        else:
            print("pvc is null")
        file_name = "./output/" + deployment["metadata"]["name"] + ".yaml"
        with open(file_name, "w") as df:
            df.write(yaml.dump(deployment))
    kustomization_yaml_creater(deployment["metadata"]["name"], data, namespace)
    print("finish creating " + deployment["metadata"]["name"] + ".yaml")

def source_reader(source_file):
    if (os.path.exists("./output") == True):
        for file in os.listdir("./output"):
            file_path = "./output/" + file
            os.remove(file_path)
    else:
        os.makedirs("./output")
    with open(source_file) as f:
        data = yaml.load(f, Loader=SafeLoader)
        kustomization_yaml_creater("", data, data["project"])
        namespace_yaml_creater(data)
        for container in data["containers"]:
            network_yaml_creater(container, data["project"])
            deployment_yaml_creater(container, data["project"])

if __name__ == '__main__':
    print("welcome k8s yaml creater")
    source_reader("source.yaml")