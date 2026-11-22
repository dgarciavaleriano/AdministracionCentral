import pytest
from unittest.mock import patch
from services.ai.llm import ProviderConfig, InferenceOrchestrator, ProviderConfigError
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnableWithFallbacks

def test_provider_config_loads_keys_dinamically():
    """Valida que ProviderConfig carga N llaves y se detiene correctamente."""
    mock_env = {
        "TEST_API_KEY_1": "token_1",
        "TEST_API_KEY_2": "token_2"
    }
    
    with patch.dict("os.environ", mock_env, clear=True):
        config = ProviderConfig(
            provider_id="groq",
            model_name="llama3-70b", 
            env_prefix="TEST_API_KEY"
        )
        instances = config.create_instances()
        
        assert len(instances) == 2
        assert isinstance(instances[0], ChatGroq)
        assert instances[0].groq_api_key.get_secret_value() == "token_1"

def test_provider_config_raises_error_invalid_provider():
    """Valida que se lance error si el proveedor no está registrado en el patrón Registry."""
    with pytest.raises(ProviderConfigError, match="Proveedor 'no_existe' no registrado."):
        ProviderConfig("no_existe", "modelo", "PREFIJO")

def test_inference_orchestrator_empty_keys_raises_error():
    """Valida que el orquestador falle rápido si no se cargan configuraciones de JSON."""
    with patch.dict("os.environ", {"LLM_PROVIDERS": "[]"}, clear=True):
        orchestrator = InferenceOrchestrator()
        with pytest.raises(ProviderConfigError, match="No se inicializó ninguna instancia LLM."):
            orchestrator.build_robust_llm()

def test_inference_orchestrator_invalid_json_raises_error():
    """Valida que el orquestador gestione un JSON malformado."""
    with patch.dict("os.environ", {"LLM_PROVIDERS": "{bad_json}"}, clear=True):
        with pytest.raises(ProviderConfigError, match="LLM_PROVIDERS no contiene un JSON válido."):
            InferenceOrchestrator()

def test_inference_orchestrator_builds_fallback_chain():
    """Valida que se ensambla el modelo principal con la cascada de fallbacks."""
    mock_env = {
        "LLM_PROVIDERS": '[{"provider": "groq", "model": "llama", "prefix": "GROQ_API_KEY"}, {"provider": "gemini", "model": "flash", "prefix": "GEMINI_API_KEY"}]',
        "GROQ_API_KEY_1": "groq_1",
        "GEMINI_API_KEY_1": "gemini_1"
    }
    
    with patch.dict("os.environ", mock_env, clear=True):
        orchestrator = InferenceOrchestrator()
        robust_llm = orchestrator.build_robust_llm()
        
        # El objeto devuelto es un ejecutable encapsulado de LangChain
        assert isinstance(robust_llm, RunnableWithFallbacks)
        
        # Verificamos que el primer fallback en la lista corresponde a Gemini
        assert hasattr(robust_llm, "fallbacks")
        assert len(robust_llm.fallbacks) == 1
        assert robust_llm.fallbacks[0].__class__.__name__ == "ChatGoogleGenerativeAI"