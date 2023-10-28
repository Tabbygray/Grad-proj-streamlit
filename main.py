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
            
            # 결과물을 저장할 디렉토리 설정
            output_dir = os.path.join(os.getcwd(), 'Get_exhaust_results')
            
            # 디렉토리가 없다면 생성
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            # 결과물 파일 경로 설정
            output_file = os.path.join(output_dir, f'{filename}_model_{model_index}.pdbqt')
            
            with open(output_file, 'w') as f:
                f.writelines(model_lines)
            model_lines = []
        else:
            model_lines.append(line)

# 화면 좌우 분할
left_column, right_column = st.columns((2,1))

# 결과 출력 창
results_window = right_column.empty()

# 파일 업로드 위젯 생성
receptor_file = left_column.file_uploader("리셉터 파일을 업로드하세요", type=['pdbqt'])
ligand_file = left_column.file_uploader("리간드 파일을 업로드하세요", type=['pdbqt'])
ligand_list_zip = left_column.file_uploader("리간드 리스트를 업로드하세요. 타입 : Zip", type=['zip'])

# 도킹 좌표 입력 필드 생성
cord_input_cols = left_column.columns(3)
x = cord_input_cols[0].number_input('x 좌표를 입력하세요', value=55.03)
y = cord_input_cols[1].number_input('y 좌표를 입력하세요', value=63.80)
z = cord_input_cols[2].number_input('z 좌표를 입력하세요', value=37.20)

# 최적 ex값 
if 'min_exhaustiveness' not in st.session_state:
    st.session_state['min_exhaustiveness'] = "-"

total_pre_docking_time = 0
min_rmsd_time_product = None

button_cols = left_column.columns((8,2,8))
button_cols_2 = left_column.columns((2,6,10))
button_cols_3 = left_column.columns((8,2,8))

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

    # 버튼 위치 정렬용
    button_cols[0].text('Exhaustiveness 값 찾기 : ')
    button_cols[1].markdown(f"##### **{st.session_state['min_exhaustiveness']}**")

    if button_cols[2].button('Exhaustiveness 값 찾기', disabled=False):
        min_rmsd_sum = None

        # 프로그레스 바 
        progress_bar = right_column.progress(0)

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
            # left_column.download_button('Download output', file_data, file_name=output_filename, mime='application/octet-stream')

            # vina_split을 사용하여 결과물을 분리합니다.
            split_vina_output(output_filename)

            rmsd_values = []
            # Exhaustiveness 값 탐색 진행 상황 표시를 위한 progress bar
            
            for i in range(1, 10):
                # 결과물이 저장된 디렉토리 설정
                output_dir = os.path.join(os.getcwd(), 'Get_exhaust_results')
                pose_filename = os.path.join(output_dir, f'output_{exhaustiveness}.pdbqt_model_{i}.pdbqt')
                if os.path.exists(pose_filename):
                    # 각 포즈를 PyMOL 객체로 로드합니다.
                    pose_name = f'pose_{i}'
                    cmd.load(pose_filename, pose_name)

                    # align 명령어를 사용하여 RMSD를 계산합니다.
                    rmsd = cmd.align(pose_name, 'reference')[0]
                    rmsd_values.append(rmsd)
                    
                    # 오류 값 방지를 위한 구조체 제거 작업
                    cmd.delete(pose_name)

            progress_bar.progress(exhaustiveness/9)
            results_window.write(f"{exhaustiveness} / 8")
                    # 각 RMSD 값을 출력합니다.
                    # left_column.write(f'RMSD for exhaustiveness {exhaustiveness}, pose {i}: {rmsd}')

            # 평균 RMSD 값을 출력합니다.
            avg_rmsd = np.mean(rmsd_values)
            # left_column.write(f'Average RMSD for exhaustiveness {exhaustiveness}: {avg_rmsd}')
 
            # 최소 RMSD 값을 출력합니다.
            min_rmsd = np.min(rmsd_values)
            # left_column.write(f'Minimum RMSD for exhaustiveness {exhaustiveness}: {min_rmsd}')

            # 평균 RMSD와 걸린 시간의 곱을 계산합니다.
            rmsd_time_product = avg_rmsd * docking_time

            # (평균 RMSD * 걸린 시간)이 최소값인 exhaustiveness를 찾습니다.
            if min_rmsd_time_product is None or rmsd_time_product < min_rmsd_time_product:
                min_rmsd_time_product = rmsd_time_product
                st.session_state['min_exhaustiveness'] = exhaustiveness

        # 가장 낮은 RMSD 합을 갖는 exhaustiveness를 출력합니다.
        # left_column.write(f"Exhaustiveness with minimum sum of average and minimum RMSD: {st.session_state['min_exhaustiveness']}")
        # left_column.markdown(f"## **{st.session_state['min_exhaustiveness']}**")
        
        button_cols[1].markdown(f"##### **{st.session_state['min_exhaustiveness']}**")
else:
    button_cols[2].button('Exhaustiveness 값 찾기', disabled=True)

if ligand_list_zip is not None :
    
    if button_cols_2[2].button("지정 exhaustiveness 값으로 docking 진행"):
        start_time = time.time() # 시간 측정 시작
        with zipfile.ZipFile(ligand_list_zip, 'r') as zip:
            num_files = len(zip.namelist())
            left_column.write(f'The ZIP file contains {num_files} files.')
            
            zip.extractall('ligands')
            for idx, filename in enumerate(os.listdir('ligands')):
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

                        with results_window.container():
                            st.write(f"파일 도킹 완료 : {filename}, 진행 상황: {idx + 1}/{num_files}")
                            st.progress((idx + 1) / num_files)  # 퍼센트 표시 추가 
                    except Exception as e :
                        print(f"An error occurred with ligand {filename}: {e}")
                        with results_window.container():
                            st.write(f"도킹 도중 에러발생 : {filename}: {e}, 진행 상황: {idx + 1}/{num_files}")
                            st.progress((idx + 1) / num_files)  # 퍼센트 표시 추가 
                        continue
        end_time = time.time()  # 시간 측정 종료
        elapsed_time = end_time - start_time  # 경과 시간 계산

        with results_window.container():
            st.write(f"전체 도킹 완료")

        # 경과 시간을 results 폴더의 time.txt 파일에 저장
        with open('results/time.txt', 'w') as f:
            f.write(f'Elapsed time: {elapsed_time} seconds')
        
        if os.path.exists('results'):
            # 'results' 폴더의 모든 파일을 zip 파일로 압축
            with zipfile.ZipFile('results.zip', 'w') as zipf:
                for root, dirs, files in os.walk('results'):
                    for file in files:
                        zipf.write(os.path.join(root, file))

            # zip 파일이 존재하는 경우에만 다운로드 버튼 생성
            if os.path.exists('results.zip'):
                # zip 파일 읽기
                with open('results.zip', 'rb') as f:
                    zip_data = f.read()

                # 결과 다운로드 버튼 생성
                button_cols_3[2].download_button('도킹 결과 다운로드', zip_data, file_name='results.zip', mime='application/zip')
