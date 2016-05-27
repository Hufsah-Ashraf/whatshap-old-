import tempfile
import os
import shutil
import pysam
from nose.tools import raises

from whatshap.__main__ import run_whatshap
from whatshap.vcf import VcfReader, VariantCallPhase


def test_pysam_version():
	from pysam import __version__ as pysam_version
	from distutils.version import LooseVersion
	assert LooseVersion(pysam_version) >= LooseVersion("0.8.1")


def test_one_variant():
	run_whatshap(phase_input_files=['tests/data/oneread.bam'], variant_file='tests/data/onevariant.vcf',
		output='/dev/null')


def test_default_output():
	"""Output to stdout"""
	run_whatshap(phase_input_files=['tests/data/oneread.bam'], variant_file='tests/data/onevariant.vcf')


def test_bam_without_readgroup():
	run_whatshap(phase_input_files=['tests/data/no-readgroup.bam'], variant_file='tests/data/onevariant.vcf',
		output='/dev/null', ignore_read_groups=True)


@raises(SystemExit)
def test_requested_sample_not_found():
	run_whatshap(phase_input_files=['tests/data/oneread.bam'], variant_file='tests/data/onevariant.vcf',
		output='/dev/null', samples=['DOES_NOT_EXIST'])


def assert_phasing(phases, expected_phases):
	print('assert_phasing({}, {})'.format(phases, expected_phases))
	assert len(phases) == len(expected_phases)
	p_unchanged = []
	p_inverted = []
	p_expected = []
	for phase, expected_phase in zip(phases, expected_phases):
		if (phase is None) and (expected_phase is None):
			continue
		assert phase.block_id == expected_phase.block_id
		p_unchanged.append(phase.phase)
		p_inverted.append(1-phase.phase)
		p_expected.append(expected_phase.phase)
	assert (p_unchanged == p_expected) or (p_inverted == p_expected)


def test_phase_three_individuals():
	tempdir = tempfile.mkdtemp()
	try:
		bamfile = tempdir + '/trio.pacbio.bam'
		outvcf = tempdir + '/output.vcf'
		pysam.view('tests/data/trio.pacbio.sam', '-Sb', '-o', bamfile, catch_stdout=False)
		pysam.index(bamfile, catch_stdout=False)
		run_whatshap(phase_input_files=[bamfile], variant_file='tests/data/trio.vcf', output=outvcf)
		assert os.path.isfile(outvcf)

		tables = list(VcfReader(outvcf))
		assert len(tables) == 1
		table = tables[0]
		assert table.chromosome == '1'
		assert len(table.variants) == 5
		assert table.samples == ['HG004', 'HG003', 'HG002']

		assert_phasing(table.phases_of('HG004'), [None, VariantCallPhase(60907394,0,None), VariantCallPhase(60907394,0,None), VariantCallPhase(60907394,0,None), None])
		assert_phasing(table.phases_of('HG003'), [VariantCallPhase(60906167,0,None), None, VariantCallPhase(60906167,0,None), None, None])
		assert_phasing(table.phases_of('HG002'), [None, None, None, None, None])

	finally:
		shutil.rmtree(tempdir)


def test_phase_one_of_three_individuals():
	tempdir = tempfile.mkdtemp()
	try:
		bamfile = tempdir + '/trio.pacbio.bam'
		outvcf = tempdir + '/output.vcf'
		pysam.view('tests/data/trio.pacbio.sam', '-Sb', '-o', bamfile, catch_stdout=False)
		pysam.index(bamfile, catch_stdout=False)
		run_whatshap(bam=[bamfile], vcf='tests/data/trio.vcf', output=outvcf, sample='HG003')
		assert os.path.isfile(outvcf)

		tables = list(VcfReader(outvcf))
		assert len(tables) == 1
		table = tables[0]
		assert table.chromosome == '1'
		assert len(table.variants) == 5
		assert table.samples == ['HG004', 'HG003', 'HG002']

		assert_phasing(table.phases_of('HG004'), [None, None, None, None, None])
		assert_phasing(table.phases_of('HG003'), [(60906167,0), None, (60906167,0), None, None])
		assert_phasing(table.phases_of('HG002'), [None, None, None, None, None])

	finally:
		shutil.rmtree(tempdir)


def test_phase_trio():
	tempdir = tempfile.mkdtemp()
	try:
		bamfile = tempdir + '/trio.pacbio.bam'
		outvcf = tempdir + '/output.vcf'
		pysam.view('tests/data/trio.pacbio.sam', '-Sb', '-o', bamfile, catch_stdout=False)
		pysam.index(bamfile, catch_stdout=False)
		run_whatshap(phase_input_files=[bamfile], variant_file='tests/data/trio.vcf', output=outvcf, ped='tests/data/trio.ped', genmap='tests/data/trio.map')
		assert os.path.isfile(outvcf)

		tables = list(VcfReader(outvcf))
		assert len(tables) == 1
		table = tables[0]
		assert table.chromosome == '1'
		assert len(table.variants) == 5
		assert table.samples == ['HG004', 'HG003', 'HG002']

		assert_phasing(table.phases_of('HG004'), [VariantCallPhase(60906167,0,None), VariantCallPhase(60906167,0,None), VariantCallPhase(60906167,0,None), VariantCallPhase(60906167,0,None), VariantCallPhase(60906167,0,None)])
		assert_phasing(table.phases_of('HG003'), [VariantCallPhase(60906167,0,None), None, VariantCallPhase(60906167,0,None), VariantCallPhase(60906167,0,None), VariantCallPhase(60906167,0,None)])
		assert_phasing(table.phases_of('HG002'), [None, VariantCallPhase(60906167,0,None), None, None, None])

	finally:
		shutil.rmtree(tempdir)


def test_phase_trio_merged_blocks():
	tempdir = tempfile.mkdtemp()
	try:
		bamfile = tempdir + '/trio-merged-blocks.bam'
		outvcf = tempdir + '/output-merged-blocks.vcf'
		pysam.view('tests/data/trio-merged-blocks.sam', '-Sb', '-o', bamfile, catch_stdout=False)
		pysam.index(bamfile, catch_stdout=False)
		run_whatshap(phase_input_files=[bamfile], variant_file='tests/data/trio-merged-blocks.vcf', output=outvcf, ped='tests/data/trio.ped', genmap='tests/data/trio.map')
		assert os.path.isfile(outvcf)

		tables = list(VcfReader(outvcf))
		assert len(tables) == 1
		table = tables[0]
		assert table.chromosome == '1'
		assert len(table.variants) == 8
		assert table.samples == ['HG002', 'HG003', 'HG004']
		assert table.num_of_blocks_of('HG004') == 1
		assert table.num_of_blocks_of('HG003') == 1
		assert table.num_of_blocks_of('HG002') == 1

		assert_phasing(table.phases_of('HG004'), [VariantCallPhase(752566,1,None), VariantCallPhase(752566,1,None), VariantCallPhase(752566,1,None), None, VariantCallPhase(752566,1,None), VariantCallPhase(752566,1,None), VariantCallPhase(752566,1,None), VariantCallPhase(752566,1,None)])
		assert_phasing(table.phases_of('HG003'), [None, None, None, None, VariantCallPhase(752566,0,None), VariantCallPhase(752566,0,None), VariantCallPhase(752566,0,None), VariantCallPhase(752566,1,None)])
		assert_phasing(table.phases_of('HG002'), [None, None, None, None, None, None, None, VariantCallPhase(752566,1,None)])

	finally:
		shutil.rmtree(tempdir)


def test_phase_trio_dont_merge_blocks():
	tempdir = tempfile.mkdtemp()
	try:
		bamfile = tempdir + '/trio-merged-blocks.bam'
		outvcf = tempdir + '/output-merged-blocks.vcf'
		pysam.view('tests/data/trio-merged-blocks.sam', '-Sb', '-o', bamfile, catch_stdout=False)
		pysam.index(bamfile, catch_stdout=False)
		run_whatshap(phase_input_files=[bamfile], variant_file='tests/data/trio-merged-blocks.vcf', output=outvcf, ped='tests/data/trio.ped', genmap='tests/data/trio.map', genetic_haplotyping=False)
		assert os.path.isfile(outvcf)

		tables = list(VcfReader(outvcf))
		assert len(tables) == 1
		table = tables[0]
		assert table.chromosome == '1'
		assert len(table.variants) == 8
		assert table.samples == ['HG002', 'HG003', 'HG004']
		assert table.num_of_blocks_of('HG004') == 2
		assert table.num_of_blocks_of('HG003') == 1
		assert table.num_of_blocks_of('HG002') == 1

		assert_phasing(table.phases_of('HG004'), [VariantCallPhase(752566,1,None), VariantCallPhase(752566,1,None), VariantCallPhase(752566,1,None), None, VariantCallPhase(853954,1,None), VariantCallPhase(853954,1,None), VariantCallPhase(853954,1,None), VariantCallPhase(853954,1,None)])
		assert_phasing(table.phases_of('HG003'), [None, None, None, None, VariantCallPhase(853954,0,None), VariantCallPhase(853954,0,None), VariantCallPhase(853954,0,None), VariantCallPhase(853954,1,None)])
		assert_phasing(table.phases_of('HG002'), [None, None, None, None, None, None, None, VariantCallPhase(853954,1,None)])

	finally:
		shutil.rmtree(tempdir)


def test_phase_mendelian_conflict():
	tempdir = tempfile.mkdtemp()
	try:
		bamfile = tempdir + '/trio.pacbio.bam'
		outvcf = tempdir + '/output.vcf'
		pysam.view('tests/data/trio.pacbio.sam', '-Sb', '-o', bamfile, catch_stdout=False)
		pysam.index(bamfile, catch_stdout=False)
		run_whatshap(phase_input_files=[bamfile], variant_file='tests/data/trio-mendelian-conflict.vcf', output=outvcf, ped='tests/data/trio.ped', genmap='tests/data/trio.map')
		assert os.path.isfile(outvcf)

		tables = list(VcfReader(outvcf))
		assert len(tables) == 1
		table = tables[0]
		assert table.chromosome == '1'
		assert len(table.variants) == 5
		assert table.samples == ['HG004', 'HG003', 'HG002']

		assert_phasing(table.phases_of('HG004'), [VariantCallPhase(60906167,0,None), None, VariantCallPhase(60906167,0,None), VariantCallPhase(60906167,0,None), VariantCallPhase(60906167,0,None)])
		assert_phasing(table.phases_of('HG003'), [VariantCallPhase(60906167,0,None), None, VariantCallPhase(60906167,0,None), VariantCallPhase(60906167,0,None), VariantCallPhase(60906167,0,None)])
		assert_phasing(table.phases_of('HG002'), [None, None, None, None, None])

	finally:
		shutil.rmtree(tempdir)


def test_phase_missing_genotypes():
	tempdir = tempfile.mkdtemp()
	try:
		bamfile = tempdir + '/trio.pacbio.bam'
		outvcf = tempdir + '/output.vcf'
		pysam.view('tests/data/trio.pacbio.sam', '-Sb', '-o', bamfile, catch_stdout=False)
		pysam.index(bamfile, catch_stdout=False)
		run_whatshap(phase_input_files=[bamfile], variant_file='tests/data/trio-missing-genotypes.vcf', output=outvcf, ped='tests/data/trio.ped', genmap='tests/data/trio.map')
		assert os.path.isfile(outvcf)

		tables = list(VcfReader(outvcf))
		assert len(tables) == 1
		table = tables[0]
		assert table.chromosome == '1'
		assert len(table.variants) == 5
		assert table.samples == ['HG004', 'HG003', 'HG002']

		assert_phasing(table.phases_of('HG004'), [VariantCallPhase(60906167,0,None), VariantCallPhase(60906167,0,None), None, VariantCallPhase(60906167,0,None), None])
		assert_phasing(table.phases_of('HG003'), [VariantCallPhase(60906167,0,None), None, None, VariantCallPhase(60906167,0,None), None])
		assert_phasing(table.phases_of('HG002'), [None, VariantCallPhase(60906167,0,None), None, None, None])

	finally:
		shutil.rmtree(tempdir)
