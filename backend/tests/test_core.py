import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import os
os.environ['DATABASE_URL']='sqlite+pysqlite:///:memory:'
from app.services import extract,truth_check,WEIGHTS

def test_job_dna_extract():
 d=extract('Senior Security Architect. Required: AWS, zero trust. Leadership and governance.')
 assert d['role_family']=='Security Architecture'; assert 'aws' in d['technologies']; assert d['seniority']=='Senior'
def test_weights_sum(): assert round(sum(WEIGHTS.values()),5)==1
def test_truth_gate_flags_unknown():
 r=truth_check('I invented a quantum teleportation company.',[]); assert r['status']=='REVIEW'
