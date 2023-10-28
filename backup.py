"""
# streamlit_app.py
import streamlit as st
from vina import Vina
import os
from pymol import cmd 

# 파일 업로드 위젯 생성
receptor_file = st.file_uploader("리셉터 파일을 업로드하세요", type=['pdbqt'])
ligand_file = st.file_uploader("리간드 파일을 업로드하세요", type=['pdbqt'])

# 도킹 좌표 입력 필드 생성
x = st.number_input('x 좌표를 입력하세요')
y = st.number_input('y 좌표를 입력하세요')
z = st.number_input('z 좌표를 입력하세요')

# exhaustiveness 입력 필드 생성
exhaustiveness = st.number_input('exhaustiveness 값을 입력하세요', min_value=1)

if receptor_file is not None and ligand_file is not None:
    # 파일 저장
    with open('receptor.pdbqt', 'wb') as f:
        f.write(receptor_file.getbuffer())
    with open('ligand.pdbqt', 'wb') as f:
        f.write(ligand_file.getbuffer())

    # Vina 객체 생성
    v = Vina(sf_name='vina')
    v.set_receptor('receptor.pdbqt')
    v.set_ligand_from_file('ligand.pdbqt')

    if st.button('Run script'):
        # 도킹 수행
        with st.spinner('Vina is running...'):
            v.compute_vina_maps(center=[x, y, z], box_size=[20, 20, 20])
            v.dock(exhaustiveness=exhaustiveness, n_poses=20)

        # 결과 저장
        v.write_poses('output.pdbqt', n_poses=5, overwrite=True)

        # 결과 파일 읽기
        with open('output.pdbqt', 'rb') as f:
            file_data = f.read()

        # 결과 다운로드 버튼 생성
        st.download_button('Download output', file_data, file_name='output.pdbqt', mime='application/octet-stream')
"""
# streamlit_app.py
import streamlit as st
from vina import Vina
import os
from pymol import cmd 

# 파일 업로드 위젯 생성
receptor_file = st.file_uploader("리셉터 파일을 업로드하세요", type=['pdbqt'])
ligand_file = st.file_uploader("리간드 파일을 업로드하세요", type=['pdbqt'])

# 도킹 좌표 입력 필드 생성
x = st.number_input('x 좌표를 입력하세요')
y = st.number_input('y 좌표를 입력하세요')
z = st.number_input('z 좌표를 입력하세요')

if receptor_file is not None and ligand_file is not None:
    # 파일 저장
    with open('receptor.pdbqt', 'wb') as f:
        f.write(receptor_file.getbuffer())
    with open('ligand.pdbqt', 'wb') as f:
        f.write(ligand_file.getbuffer())

    # Vina 객체 생성
    v = Vina(sf_name='vina')
    v.set_receptor('receptor.pdbqt')
    v.set_ligand_from_file('ligand.pdbqt')

    # 기준이 될 구조를 로드합니다.
    cmd.load('ligand.pdbqt', 'reference')

    if st.button('Run script'):
        for exhaustiveness in range(1, 9):
            # 도킹 수행
            v.compute_vina_maps(center=[x, y, z], box_size=[20, 20, 20])
            v.dock(exhaustiveness=exhaustiveness, n_poses=20)

            # 결과 저장
            output_filename = f'output_{exhaustiveness}.pdbqt'
            v.write_poses(output_filename, n_poses=1, overwrite=True)

            # 결과 파일 읽기
            with open(output_filename, 'rb') as f:
                file_data = f.read()

            # 결과 다운로드 버튼 생성
            st.download_button('Download output', file_data, file_name=output_filename, mime='application/octet-stream')

            # 결과물을 PyMOL 객체로 로드합니다.
            structure_name = f'exhaustiveness_{exhaustiveness}'
            cmd.load(output_filename, structure_name)

            # align 명령어를 사용하여 RMSD를 계산합니다.
            rmsd = cmd.align(structure_name, 'reference')[0]
            
            # RMSD 값을 출력합니다.
            st.write(f'RMSD for exhaustiveness {exhaustiveness}: {rmsd}')


# streamlit_app.py
import streamlit as st
from vina import Vina
import os
from pymol import cmd 
import numpy as np

# Vina 결과를 분리하는 함수
def split_vina_output(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()

    model_lines = []
    model_index = 0
    for line in lines:
        if line.startswith('MODEL'):
            model_index += 1
            model_lines.append(line)
        elif line.startswith('ENDMDL'):
            model_lines.append(line)
            with open(f'model_{model_index}.pdbqt', 'w') as f:
                f.writelines(model_lines)
            model_lines = []
        else:
            model_lines.append(line)

# 파일 업로드 위젯 생성
receptor_file = st.file_uploader("리셉터 파일을 업로드하세요", type=['pdbqt'])
ligand_file = st.file_uploader("리간드 파일을 업로드하세요", type=['pdbqt'])

# 도킹 좌표 입력 필드 생성
x = st.number_input('x 좌표를 입력하세요')
y = st.number_input('y 좌표를 입력하세요')
z = st.number_input('z 좌표를 입력하세요')

if receptor_file is not None and ligand_file is not None:
    # 파일 저장
    with open('receptor.pdbqt', 'wb') as f:
        f.write(receptor_file.getbuffer())
    with open('ligand.pdbqt', 'wb') as f:
        f.write(ligand_file.getbuffer())

    # Vina 객체 생성
    v = Vina(sf_name='vina')
    v.set_receptor('receptor.pdbqt')
    v.set_ligand_from_file('ligand.pdbqt')

    # 기준이 될 구조를 로드합니다.
    cmd.load('ligand.pdbqt', 'reference')

    if st.button('Run script'):
        for exhaustiveness in range(1, 9):
            # 도킹 수행
            v.compute_vina_maps(center=[x, y, z], box_size=[20, 20, 20])
            v.dock(exhaustiveness=exhaustiveness, n_poses=9)

            # 결과 저장
            output_filename = f'output_{exhaustiveness}.pdbqt'
            v.write_poses(output_filename, n_poses=9, overwrite=True)

            # 결과 파일 읽기
            with open(output_filename, 'rb') as f:
                file_data = f.read()

            # 결과 다운로드 버튼 생성
            st.download_button('Download output', file_data, file_name=output_filename, mime='application/octet-stream')

            # vina_split을 사용하여 결과물을 분리합니다.
            split_vina_output(output_filename)
            
            rmsd_values = []
            for i in range(1, 10):
                pose_filename = f'model_{i}.pdbqt'
                if os.path.exists(pose_filename):
                    # 각 포즈를 PyMOL 객체로 로드합니다.
                    pose_name = f'pose_{i}'
                    cmd.load(pose_filename, pose_name)

                    # align 명령어를 사용하여 RMSD를 계산합니다.
                    rmsd = cmd.align(pose_name, 'reference')[0]
                    rmsd_values.append(rmsd)
                    
                    # 각 RMSD 값을 출력합니다.
                    st.write(f'RMSD for exhaustiveness {exhaustiveness}, pose {i}: {rmsd}')
            
            # 평균 RMSD 값을 출력합니다.
            st.write(f'Average RMSD for exhaustiveness {exhaustiveness}: {np.mean(rmsd_values)}')

            # 최소 RMSD 값을 출력합니다.
            st.write(f'Minimum RMSD for exhaustiveness {exhaustiveness}: {np.min(rmsd_values)}')

"""
if st.button("TEST"):
    # 단백질 구조를 로드합니다.
    cmd.load('output_ligand_5.pdbqt', 'prot1')
    cmd.load('vildagliptin_from_3w2t.pdbqt', 'prot2')

    # cmd.align을 사용하여 RMSD를 계산합니다.
    rmsd_align = cmd.align('prot1', 'prot2')[0]

    st.write(f'RMSD calculated with cmd.align: {rmsd_align}')

    # cmd.rms_cur을 사용하여 RMSD를 계산합니다.
    #cmd.super('prot1', 'prot2')  # superimpose structures
    rmsd_cur = cmd.rms_cur('prot1', 'prot2')

    st.write(f'RMSD calculated with cmd.rms_cur: {rmsd_cur}')
"""

""" Stable version 1.0
# streamlit_app.py
import streamlit as st
from vina import Vina
import os
from pymol import cmd 
import numpy as np
import zipfile
import time 

# Vina 결과를 분리하는 함수
def split_vina_output(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()

    model_lines = []
    model_index = 0
    for line in lines:
        if line.startswith('MODEL'):
            model_index += 1
            model_lines.append(line)
        elif line.startswith('ENDMDL'):
            model_lines.append(line)
            with open(f'{filename}_model_{model_index}.pdbqt', 'w') as f:
                f.writelines(model_lines)
            model_lines = []
        else:
            model_lines.append(line)

# 파일 업로드 위젯 생성
receptor_file = st.file_uploader("리셉터 파일을 업로드하세요", type=['pdbqt'])
ligand_file = st.file_uploader("리간드 파일을 업로드하세요", type=['pdbqt'])
ligand_list_zip = st.file_uploader("리간드 리스트를 업로드하세요. 타입 : Zip", type=['zip'])

# 도킹 좌표 입력 필드 생성
x = st.number_input('x 좌표를 입력하세요', value=55.03)
y = st.number_input('y 좌표를 입력하세요', value=63.80)
z = st.number_input('z 좌표를 입력하세요', value=37.20)

if 'min_exhaustiveness' not in st.session_state:
    st.session_state['min_exhaustiveness'] = None

total_pre_docking_time = 0
min_rmsd_time_product = None

if receptor_file is not None and ligand_file is not None:
    # 파일 저장
    with open('receptor.pdbqt', 'wb') as f:
        f.write(receptor_file.getbuffer())
    with open('ligand.pdbqt', 'wb') as f:
        f.write(ligand_file.getbuffer())

    # Vina 객체 생성
    v = Vina(sf_name='vina')
    v.set_receptor('receptor.pdbqt')
    v.set_ligand_from_file('ligand.pdbqt')

    # 기준이 될 구조를 로드합니다.
    cmd.load('ligand.pdbqt', 'reference')

    if st.button('Run script'):
        min_rmsd_sum = None

        for exhaustiveness in range(1, 9):
            # 도킹 수행
            v.compute_vina_maps(center=[x, y, z], box_size=[20, 20, 20])
            vina_start_time = time.time()
            v.dock(exhaustiveness=exhaustiveness)
            vina_end_time = time.time()
            docking_time = vina_end_time - vina_start_time

            # 결과 저장
            output_filename = f'output_{exhaustiveness}.pdbqt'
            v.write_poses(output_filename, overwrite=True)

            # 수행 시간 저장
            total_pre_docking_time += docking_time
            with open(f'results/exhaustiveness : {exhaustiveness} docking time.txt', 'w') as f:
                f.write(f'Elapsed time: {docking_time} seconds')

            # 결과 파일 읽기
            with open(output_filename, 'rb') as f:
                file_data = f.read()

            # 결과 다운로드 버튼 생성
            st.download_button('Download output', file_data, file_name=output_filename, mime='application/octet-stream')

            # vina_split을 사용하여 결과물을 분리합니다.
            split_vina_output(output_filename)

            rmsd_values = []
            for i in range(1, 10):
                pose_filename = f'output_{exhaustiveness}.pdbqt_model_{i}.pdbqt'
                if os.path.exists(pose_filename):
                    # 각 포즈를 PyMOL 객체로 로드합니다.
                    pose_name = f'pose_{i}'
                    cmd.load(pose_filename, pose_name)

                    # align 명령어를 사용하여 RMSD를 계산합니다.
                    rmsd = cmd.align(pose_name, 'reference')[0]
                    rmsd_values.append(rmsd)
                    
                    cmd.delete(pose_name)

                    # 각 RMSD 값을 출력합니다.
                    st.write(f'RMSD for exhaustiveness {exhaustiveness}, pose {i}: {rmsd}')

            # 평균 RMSD 값을 출력합니다.
            avg_rmsd = np.mean(rmsd_values)
            st.write(f'Average RMSD for exhaustiveness {exhaustiveness}: {avg_rmsd}')

            # 최소 RMSD 값을 출력합니다.
            min_rmsd = np.min(rmsd_values)
            st.write(f'Minimum RMSD for exhaustiveness {exhaustiveness}: {min_rmsd}')

            # 평균 RMSD와 걸린 시간의 곱을 계산합니다.
            rmsd_time_product = avg_rmsd * docking_time
            # 최소 평균 RMSD * 걸린 시간을 갖는 exhaustiveness를 찾습니다.
            if min_rmsd_time_product is None or rmsd_time_product < min_rmsd_time_product:
                min_rmsd_time_product = rmsd_time_product
                st.session_state['min_exhaustiveness'] = exhaustiveness

        # 가장 낮은 RMSD 합을 갖는 exhaustiveness를 출력합니다.
        st.write(f"Exhaustiveness with minimum sum of average and minimum RMSD: {st.session_state['min_exhaustiveness']}")
        st.markdown(f"## **{st.session_state['min_exhaustiveness']}**")

if ligand_list_zip is not None:
    if st.button("지정 exhaustiveness 값으로 docking 진행"):
        start_time = time.time() # 시간 측정 시작
        with zipfile.ZipFile(ligand_list_zip, 'r') as zip:
            num_files = len(zip.namelist())
            st.write(f'The ZIP file contains {num_files} files.')
            
            zip.extractall('ligands')
            for filename in os.listdir('ligands'):
                if filename.endswith('pdbqt'):
                    ligand_file = os.path.join('ligands', filename)
                    print(ligand_file)
                    try:
                        # 리셉터 로드 
                        v.set_receptor('receptor.pdbqt')
                        # 리간드 로드
                        v.set_ligand_from_file(ligand_file)

                        # 도킹 수행
                        v.compute_vina_maps(center=[x, y, z], box_size=[20, 20, 20])
                        v.dock(exhaustiveness=st.session_state['min_exhaustiveness'])

                        # 결과를 저장할 폴더 생성
                        os.makedirs('results', exist_ok=True)

                        # 결과 저장
                        output_filename = os.path.join('results', f'output_{filename}')
                        v.write_poses(output_filename, overwrite=True)
                    except Exception as e :
                        print(f"An error occurred with ligand {filename}: {e}")
                        continue
        end_time = time.time()  # 시간 측정 종료
        elapsed_time = end_time - start_time  # 경과 시간 계산

        # 경과 시간을 results 폴더의 time.txt 파일에 저장
        with open('results/time.txt', 'w') as f:
            f.write(f'Elapsed time: {elapsed_time} seconds')

"""