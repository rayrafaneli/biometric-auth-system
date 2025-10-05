import math
from typing import List, Dict, Optional

# matcher.py
# Utilitários de comparação e a política de decisão (best/mean/margin).
# Comentários rápidos e diretos: este módulo responde pela lógica que decide
# se uma captura concede acesso a um usuário.

# Defaults 'do objeto' — valores centrais que definem a política de decisão.
# Se quiser ajustar a política, altere aqui apenas.

DEFAULT_TOP_K = 3
DEFAULT_BEST_THRESHOLD = 0.91  
DEFAULT_MEAN_THRESHOLD = 0.88  
DEFAULT_MARGIN = 0.04 
DEFAULT_MIN_SAMPLES = 3

DEFAULT_METRIC = 'cosine'  # Nova opção de métrica
def _euclidean_distance(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    return 1.0 - (math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b))) / (math.sqrt(len(a)) * 2))



def _cosine_similarity(a: List[float], b: List[float]) -> float:
    # produto e norma; retorna 0.0 se algum vetor for vazio ou nulo
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def normalize_features(feats):
    """Garante que 'features' seja uma lista de vetores.

    Exemplos: [] -> [] ; [v1,v2,...] onde v1 é número -> [[v1,...]] ;
    já [[...],[...]] permanece igual.
    """
    if not feats:
        return []
    # Se é lista e o primeiro elemento é número, trata como vetor único
    first = feats[0]
    if isinstance(first, (int, float)):
        return [feats]
    # Se é lista de listas (cada elemento iterável), assume que está no formato correto
    return feats


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Wrapper público pequeno para similaridade cosseno."""
    return _cosine_similarity(a, b)


def score_users(query_feat: List[float], users_data: List[Dict], top_k: int = 3, metric: str = DEFAULT_METRIC):
    """Para cada usuário calcula:
    - best_score: a maior similaridade entre query e amostras do usuário
    - mean_top_k: média das top_k similaridades

    Retorna lista (user, best_score, mean_top_k) ordenada pelo best_score.
    Essa combinação diminui falsos positivos causados por 1 amostra isolada.
    """
    results = []
    for u in users_data:
        feats = normalize_features(u.get('features') or [])
        scores = []
        for f in feats:
            try:
                if metric == 'cosine':
                    s = _cosine_similarity(query_feat, f)
                elif metric == 'euclidean':
                    s = _euclidean_distance(query_feat, f)
                else:
                    s = _cosine_similarity(query_feat, f)
            except Exception:
                s = 0.0
            scores.append(s)

        if not scores:
            best = 0.0
            mean_top = 0.0
        else:
            scores.sort(reverse=True)
            best = scores[0]
            k = min(top_k, len(scores))
            mean_top = sum(scores[:k]) / k if k > 0 else 0.0

        results.append((u, best, mean_top))

    results.sort(key=lambda x: x[1], reverse=True)
    return results


def find_best_match(query_feat: List[float], users_data: List[Dict], metric: str = DEFAULT_METRIC) -> Optional[Dict]:
    """Encontra o usuário com maior pontuação (máximo entre as amostras).

    Entrada: users_data = [{'id','name','access_level','features'}, ...]
    Retorna {'user':..., 'score':...} ou None.
    """
    best = None
    best_score = -1.0
    for u in users_data:
        feats = u.get('features') or []
        scores = []
        for f in feats:
            if metric == 'cosine':
                s = _cosine_similarity(query_feat, f)
            elif metric == 'euclidean':
                s = _euclidean_distance(query_feat, f)
            else:
                s = _cosine_similarity(query_feat, f)
            scores.append(s)

        # Use a maior pontuação entre as amostras do usuário (menos sensível à média)
        user_score = max(scores) if scores else 0.0
        if user_score > best_score:
            best_score = user_score
            best = u

    if best is None:
        return None

    return {'user': best, 'score': best_score}


def decide_match(query_feat: List[float], users_data: List[Dict], top_k: int = DEFAULT_TOP_K,
                best_threshold: float = DEFAULT_BEST_THRESHOLD,
                mean_threshold: float = DEFAULT_MEAN_THRESHOLD,
                margin: float = DEFAULT_MARGIN,
                min_samples: int = DEFAULT_MIN_SAMPLES,
                metric: str = DEFAULT_METRIC):
    """Aplica a política de decisão combinada e devolve um resultado legível.

    Retorna: (granted, best_user, best_score, mean_top, reason, scored_list)
    - reason: texto curto em pt explicando negação (None se acesso concedido)
    - scored_list: útil para debug/print
    """
    scored = score_users(query_feat, users_data, top_k=top_k, metric=metric)
    if not scored:
        return False, None, 0.0, 0.0, 'Nenhum candidato encontrado.', scored

    best_entry = scored[0]
    second_entry = scored[1] if len(scored) > 1 else (None, 0.0, 0.0)

    best_user, best_score, mean_top = best_entry
    _, second_best_score, _ = second_entry

    candidate_feats = best_user.get('features') if best_user else []
    num_samples = len(candidate_feats) if candidate_feats else 0

    # Regras de decisão
    if not best_user:
        return False, None, 0.0, 0.0, 'Nenhum candidato encontrado.', scored
    if num_samples < min_samples:
        return False, best_user, best_score, mean_top, f"Usuário candidato tem apenas {num_samples} amostra(s); mínimo requerido = {min_samples}.", scored
    if best_score < best_threshold:
        return False, best_user, best_score, mean_top, f"Melhor similaridade ({best_score:.3f}) abaixo do limiar ({best_threshold}).", scored
    if mean_top < mean_threshold:
        return False, best_user, best_score, mean_top, f"Média top-{top_k} das similaridades ({mean_top:.3f}) abaixo do limiar ({mean_threshold}).", scored
    if (best_score - second_best_score) < margin:
        return False, best_user, best_score, mean_top, f"Margem entre top1 e top2 insuficiente ({(best_score-second_best_score):.4f} < {margin}).", scored

    # se passou por todos os testes, conceder acesso
    return True, best_user, best_score, mean_top, None, scored
