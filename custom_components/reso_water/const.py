"""Constantes pour l'intégration RESO Seine & Orge."""

DOMAIN = "reso_water"
PLATFORMS = ["sensor"]

BASE_URL = "https://ael.eauxseinebievreorge.fr/webapi"
SITE_URL = "https://ael.eauxseinebievreorge.fr/"
ACCESS_KEY = "XX_fr-5DjSDlsdMM-GOSB-PRD"
CLIENT_ID = "AEL-TOKEN-GOSB-PRD"

CONF_EMAIL = "email"
CONF_PASSWORD = "password"
CONF_CONTRAT = "contrat"

SCAN_INTERVAL_HOURS = 3

# ── Eau potable ──────────────────────────────────────────────
CONF_EP_ABONNEMENT        = "ep_abonnement_annuel_ht"   # €/an HT
CONF_EP_CONSO             = "ep_conso_m3_ht"            # €/m³ HT
CONF_EP_TVA               = "ep_tva"                    # %

DEFAULT_EP_ABONNEMENT     = 39.60   # 19,80 € HT x 2 semestres
DEFAULT_EP_CONSO          = 1.80    # €/m³ HT
DEFAULT_EP_TVA            = 5.5

# ── Assainissement ───────────────────────────────────────────
CONF_AS_TERRITORIALE      = "as_territoriale_m3_ht"     # €/m³ HT — TVA 0%
CONF_AS_SYNDICALE         = "as_syndicale_m3_ht"        # €/m³ HT — TVA 10%
CONF_AS_INTERDEP          = "as_interdep_m3_ht"         # €/m³ HT — TVA 10%

DEFAULT_AS_TERRITORIALE   = 0.7370
DEFAULT_AS_SYNDICALE      = 0.3700
DEFAULT_AS_INTERDEP       = 0.9950

# ── Organismes publics ───────────────────────────────────────
CONF_OP_VNF               = "op_vnf_m3_ht"             # €/m³ HT — TVA 5,5%
CONF_OP_EPTB              = "op_eptb_m3_ht"            # €/m³ HT — TVA 5,5%
CONF_OP_PREL_RESSOURCE    = "op_prel_ressource_m3_ht"  # €/m³ HT — TVA 5,5%
CONF_OP_AESN_CONSO        = "op_aesn_conso_m3_ht"      # €/m³ HT — TVA 5,5%
CONF_OP_AESN_PERF_EP      = "op_aesn_perf_ep_m3_ht"   # €/m³ HT — TVA 5,5%
CONF_OP_AESN_PERF_AS      = "op_aesn_perf_as_m3_ht"   # €/m³ HT — TVA 10%

DEFAULT_OP_VNF            = 0.0110
DEFAULT_OP_EPTB           = 0.0091
DEFAULT_OP_PREL_RESSOURCE = 0.0600
DEFAULT_OP_AESN_CONSO     = 0.4600
DEFAULT_OP_AESN_PERF_EP   = 0.0170
DEFAULT_OP_AESN_PERF_AS   = 0.0267

# TVA applicables
TVA_0   = 0.0
TVA_55  = 5.5
TVA_10  = 10.0
