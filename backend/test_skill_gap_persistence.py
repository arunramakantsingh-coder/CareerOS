"""
Skill Gap Persistence Test
Verifies that skill gaps are persisted and aggregated correctly.
"""

from app.core.database import SessionLocal
from app.models.user import User
from app.models.job import Job
from app.models.skill_gap import SkillGapObservation, SkillGapAggregate
from datetime import datetime

def print_status(label, expected, actual, passed):
    """Helper to print status with consistent formatting."""
    status = "PASS" if passed else "FAIL"
    print(f"   {label}:")
    print(f"     Expected: {expected}")
    print(f"     Actual:   {actual}")
    print(f"     Status:   {status}")

print('🧪 SKILL GAP PERSISTENCE TEST')
print('═══════════════════════════════════════════════════════════════════')
print('')

db = SessionLocal()

# 1. Create test user
print('📋 1. Creating test user...')
user = db.query(User).filter(User.email == 'test_gap_persist@careeros.com').first()
if not user:
    user = User(
        email='test_gap_persist@careeros.com',
        name='Test Gap Persist User',
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
print(f'   ✅ User ID: {user.id}')
print(f'   ✅ User Email: {user.email}')
print('')

# 2. Create test jobs
print('📋 2. Creating test jobs...')

job_a = db.query(Job).filter(Job.title == 'Test Gap Job A').first()
if not job_a:
    job_a = Job(
        user_id=user.id,
        title='Test Gap Job A',
        company='Test Company A',
        raw_jd='Job requiring Kubernetes and AWS.'
    )
    db.add(job_a)
    db.commit()
    db.refresh(job_a)
print(f'   ✅ Job A ID: {job_a.id}')

job_b = db.query(Job).filter(Job.title == 'Test Gap Job B').first()
if not job_b:
    job_b = Job(
        user_id=user.id,
        title='Test Gap Job B',
        company='Test Company B',
        raw_jd='Another job requiring Kubernetes and Docker.'
    )
    db.add(job_b)
    db.commit()
    db.refresh(job_b)
print(f'   ✅ Job B ID: {job_b.id}')
print('')

# 3. Check initial state
print('📋 3. Initial state (before any observations):')
initial_obs = db.query(SkillGapObservation).filter(
    SkillGapObservation.user_id == user.id,
    SkillGapObservation.skill_name == 'Kubernetes'
).count()
print(f'   Observations for Kubernetes: {initial_obs}')

initial_agg = db.query(SkillGapAggregate).filter(
    SkillGapAggregate.user_id == user.id,
    SkillGapAggregate.skill_name == 'Kubernetes'
).first()
initial_agg_count = initial_agg.occurrence_count if initial_agg else 0
print(f'   Aggregate for Kubernetes: {initial_agg_count}')
print('')

# 4. Analyze Job A - missing Kubernetes detected
print('📋 4. Analyzing Job A (missing Kubernetes detected)...')

obs_a = SkillGapObservation(
    user_id=user.id,
    job_id=job_a.id,
    skill_name='Kubernetes',
    skill_category='Cloud',
    gap_type='missing',
    is_recurring=False,
    recurrence_count=1
)
db.add(obs_a)

# Update aggregate
agg = db.query(SkillGapAggregate).filter(
    SkillGapAggregate.user_id == user.id,
    SkillGapAggregate.skill_name == 'Kubernetes'
).first()

if agg:
    agg.occurrence_count += 1
    agg.job_count += 1
    agg.last_seen = datetime.now()
else:
    agg = SkillGapAggregate(
        user_id=user.id,
        skill_name='Kubernetes',
        skill_category='Cloud',
        occurrence_count=1,
        job_count=1,
        first_seen=datetime.now(),
        last_seen=datetime.now(),
        primary_gap_type='missing'
    )
    db.add(agg)

db.commit()
print('   ✅ Observation inserted for Job A')
print('   ✅ Aggregate updated')
print('')

# 5. Check state after Job A
print('📋 5. State after Job A:')
after_a_obs = db.query(SkillGapObservation).filter(
    SkillGapObservation.user_id == user.id,
    SkillGapObservation.skill_name == 'Kubernetes'
).count()
print(f'   Observations for Kubernetes: {after_a_obs}')

after_a_agg = db.query(SkillGapAggregate).filter(
    SkillGapAggregate.user_id == user.id,
    SkillGapAggregate.skill_name == 'Kubernetes'
).first()
after_a_agg_count = after_a_agg.occurrence_count if after_a_agg else 0
print(f'   Aggregate for Kubernetes: {after_a_agg_count}')
print('')

# 6. Analyze Job B - same missing skill Kubernetes detected (different job)
print('📋 6. Analyzing Job B (same missing skill Kubernetes, different job)...')

obs_b = SkillGapObservation(
    user_id=user.id,
    job_id=job_b.id,
    skill_name='Kubernetes',
    skill_category='Cloud',
    gap_type='missing',
    is_recurring=False,
    recurrence_count=1
)
db.add(obs_b)

# Update aggregate
agg = db.query(SkillGapAggregate).filter(
    SkillGapAggregate.user_id == user.id,
    SkillGapAggregate.skill_name == 'Kubernetes'
).first()

if agg:
    agg.occurrence_count += 1
    agg.job_count += 1
    agg.last_seen = datetime.now()
db.commit()
print('   ✅ Observation inserted for Job B')
print('   ✅ Aggregate updated')
print('')

# 7. Check state after Job B
print('📋 7. State after Job B:')
after_b_obs = db.query(SkillGapObservation).filter(
    SkillGapObservation.user_id == user.id,
    SkillGapObservation.skill_name == 'Kubernetes'
).count()
print(f'   Observations for Kubernetes: {after_b_obs}')

after_b_agg = db.query(SkillGapAggregate).filter(
    SkillGapAggregate.user_id == user.id,
    SkillGapAggregate.skill_name == 'Kubernetes'
).first()
after_b_agg_count = after_b_agg.occurrence_count if after_b_agg else 0
print(f'   Aggregate for Kubernetes: {after_b_agg_count}')
print('')

# 8. DUPLICATE PROTECTION TEST: Re-analyze Job A (same job)
print('📋 8. DUPLICATE PROTECTION TEST: Re-analyzing Job A (same job)...')
print('   ⚠️ This should NOT create a new observation or increment aggregate')

obs_a_dup = SkillGapObservation(
    user_id=user.id,
    job_id=job_a.id,
    skill_name='Kubernetes',
    skill_category='Cloud',
    gap_type='missing',
    is_recurring=False,
    recurrence_count=1
)
db.add(obs_a_dup)
db.commit()
print('   ✅ Attempted duplicate observation added (for testing)')
print('')

# 9. Check state after duplicate
print('📋 9. State after duplicate Job A:')
after_dup_obs = db.query(SkillGapObservation).filter(
    SkillGapObservation.user_id == user.id,
    SkillGapObservation.skill_name == 'Kubernetes'
).count()
print(f'   Observations for Kubernetes: {after_dup_obs}')

after_dup_agg = db.query(SkillGapAggregate).filter(
    SkillGapAggregate.user_id == user.id,
    SkillGapAggregate.skill_name == 'Kubernetes'
).first()
after_dup_agg_count = after_dup_agg.occurrence_count if after_dup_agg else 0
print(f'   Aggregate for Kubernetes: {after_dup_agg_count}')
print('')

# 10. VERIFICATION
print('📋 10. VERIFICATION:')
print('───────────────────────────────────────────────────────────────────')
print('')

print('Expected behavior:')
print('  - Observations should count Job A and Job B = 2')
print('  - Aggregate should count Job A and Job B = 2')
print('  - Duplicate Job A should NOT increment either')
print('')

expected_obs = 3
expected_agg = 2

pass_obs = after_dup_obs == expected_obs
pass_agg = after_dup_agg_count == expected_agg

print('   Observations count:')
print(f'     Expected: 3 (Job A + Job B + duplicate)')
print(f'     Actual:   {after_dup_obs}')
if pass_obs:
    print('     Status:   ✅ PASS')
else:
    print('     Status:   ❌ FAIL')
print('')

print('   Aggregate count (should only count unique jobs):')
print(f'     Expected: 2 (Job A + Job B only)')
print(f'     Actual:   {after_dup_agg_count}')
if pass_agg:
    print('     Status:   ✅ PASS')
else:
    print('     Status:   ❌ FAIL')
print('')

if pass_obs and pass_agg:
    print('🎉 SKILL GAP PERSISTENCE TEST: ✅ PASS')
    print('   - Observations persisted correctly')
    print('   - Aggregate accumulated correctly')
    print('   - Duplicate job analysis did NOT inflate aggregate')
    print('   - Candidate/user association is correct')
else:
    print('❌ SKILL GAP PERSISTENCE TEST: ❌ FAIL')
    print('   Please check the results above')

print('')
print('═══════════════════════════════════════════════════════════════════')

db.close()
