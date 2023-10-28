from vina import Vina
import os

x = 55
y = 64
z = 37

v = Vina(sf_name='vina')

# 결과를 저장할 폴더 생성
os.makedirs('results_test', exist_ok=True)

# /ligands 폴더 내의 모든 .pdbqt 파일에 대해 도킹 수행
for filename in os.listdir('ligands'):
    if filename.endswith('.pdbqt'):
        ligand_file = os.path.join('ligands', filename)
        print(ligand_file)
        
        v.set_receptor('3vjm_processed.pdbqt')
        # 리간드 로드
        v.set_ligand_from_file(ligand_file)
        
        # 도킹 수행
        v.compute_vina_maps(center=[x, y, z], box_size=[20, 20, 20])
        v.dock(exhaustiveness=2)
        
        # 결과 저장
        output_filename = os.path.join('results_test', f'output_{filename}')
        v.write_poses(output_filename, overwrite=True)
