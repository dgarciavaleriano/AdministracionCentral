import os
import json
from pydantic import SecretStr
from typing import List, Type, Dict
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

class ProviderConfigError(Exception):
    """Excepción personalizada para errores de configuración de proveedores LLM."""
    pass

# Patrón Registry: Desacopla las cadenas de texto de las clases importadas
PROVIDER_REGISTRY: Dict[str, Type[BaseChatModel]] = {
    "groq": ChatGroq,
    "gemini": ChatGoogleGenerativeAI,
    "openai": ChatOpenAI
}

class ProviderConfig:
    """
    Encapsula la configuración y creación de instancias de un proveedor específico.
    
    Extrae dinámicamente las API keys del entorno y genera una lista de 
    instancias del modelo correspondiente listas para ser utilizadas.
    """
    def __init__(self, provider_id: str, model_name: str, env_prefix: str):
        """
        Inicializa la configuración del proveedor.

        Args:
            provider_id (str): Identificador del proveedor en el PROVIDER_REGISTRY (ej. 'groq').
            model_name (str): Nombre exacto del modelo a instanciar (ej. 'llama3-70b-8192').
            env_prefix (str): Prefijo de la variable de entorno que contiene las API keys (ej. 'GROQ_API_KEY').
            
        Raises:
            ProviderConfigError: Si el `provider_id` no existe en el registro.
        """
        self.model_class = PROVIDER_REGISTRY.get(provider_id.lower())
        if not self.model_class:
            raise ProviderConfigError(f"Proveedor '{provider_id}' no registrado.")
        self.model_name = model_name
        self.env_prefix = env_prefix

    def create_instances(self) -> List[BaseChatModel]:
        """
        Crea instancias del modelo iterando sobre variables de entorno numeradas.

        Busca en `os.environ` variables con el formato `{env_prefix}_{i}` (ej. GROQ_API_KEY_1).
        El bucle se detiene cuando no encuentra la siguiente secuencia numérica.

        Returns:
            List[BaseChatModel]: Lista de clientes LLM instanciados y securizados con SecretStr.
        """
        instances = []
        i = 1
        while True:
            env_var = f"{self.env_prefix}_{i}"
            key = os.environ.get(env_var, "").strip()
            if not key:
                break
            instances.append(self.model_class(api_key=SecretStr(key), model=self.model_name))
            i += 1
        return instances

class InferenceOrchestrator:
    """
    Orquesta la resiliencia de los modelos aplicando composición y fallbacks dinámicos.
    
    Carga la configuración de proveedores desde la variable de entorno `LLM_PROVIDERS` 
    (formato JSON) y construye una cadena LangChain con tolerancia a fallos.
    """
    def __init__(self):
        """
        Inicializa el orquestador decodificando la variable `LLM_PROVIDERS`.
        
        Raises:
            ProviderConfigError: Si `LLM_PROVIDERS` no contiene un JSON válido.
        """
        config_str = os.environ.get("LLM_PROVIDERS", "[]")
        try:
            configs = json.loads(config_str)
        except json.JSONDecodeError:
            raise ProviderConfigError("LLM_PROVIDERS no contiene un JSON válido.")
            
        self.providers = [
            ProviderConfig(c["provider"], c["model"], c["prefix"])
            for c in configs
        ]

    def build_robust_llm(self) -> BaseChatModel:
        """
        Construye el modelo principal con su cascada de respaldo (fallbacks).

        Extrae todas las instancias de los proveedores configurados y las encadena
        usando el método `.with_fallbacks()`. Ante un error (ej. límite de cuota),
        LangChain saltará automáticamente al siguiente proveedor de la lista.

        Returns:
            BaseChatModel: Un ejecutable LangChain (`RunnableWithFallbacks`) listo para inferencia.
            
        Raises:
            ProviderConfigError: Si no se pudo cargar ninguna instancia con claves válidas.
        """
        instances = []
        for provider in self.providers:
            instances.extend(provider.create_instances())
        
        if not instances:
            raise ProviderConfigError("No se inicializó ninguna instancia LLM.")
        
        primary_llm = instances[0]
        fallbacks = instances[1:]
        
        return primary_llm.with_fallbacks(fallbacks)