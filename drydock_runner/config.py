from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, List


class StaticIP(BaseModel):
    address: str
    gateway: str
    nameservers: List[str]


class Network(BaseModel):
    vlanID: int
    staticIP: StaticIP
    cidr: str
    gateway: str


class Discovery(BaseModel):
    enabled: bool = True
    method: str = Field("dhcp-scan", pattern="^dhcp-scan$")
    timeoutSeconds: int = 120


class InauguralNode(BaseModel):
    sshUser: str = "ubuntu"
    sshPassword: str
    hostname: Optional[str] = None


class RepositoryPaths(BaseModel):
    kubeadmConfig: Optional[str] = None
    argocdManifest: Optional[str] = None
    argocdValues: Optional[str] = None
    discoverPxe: Optional[str] = None


class RepositorySource(BaseModel):
    url: HttpUrl
    branch: Optional[str] = "main"
    paths: RepositoryPaths


class BootstrapSources(BaseModel):
    repositories: Dict[str, RepositorySource]


class BootstrapSpec(BaseModel):
    network: Network
    discovery: Discovery
    inauguralNode: InauguralNode
    bootstrapSources: BootstrapSources


class Metadata(BaseModel):
    name: str
    namespace: Optional[str]


class BootstrapConfig(BaseModel):
    apiVersion: str
    kind: str
    metadata: Metadata
    spec: BootstrapSpec
    status: Optional[dict] = None
