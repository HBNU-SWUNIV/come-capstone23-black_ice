import sys
import peewee
import argparse
import datetime
from typing import List
import cv2 as cv
import numpy as np
#import traceback

import datatables
from _utils import form_check




def print_dict_formatted(dict_format_data):
    formatted_data = []
    for key, value in dict_format_data.items():
        formatted_data.append(f'{key}: {value}')
    result = ', '.join(formatted_data)
    return result



def print_query_results(query):
    for row in query:
        for i in row:
            print(i, end=' ')
        print('',end='\n')



def query_parse(query, colums = List[str]) -> List:
    '''
    입력받은 데이터에서 지정한 컬럼들을 선택함, 순서는 입력받은 컬럼명 대로
    지정한 컬럼명이 없을 시 오류
    '''
    result_list = []
    t = []
    for row in query:
        #t.append(getattr(row, 'daytime')) # 출력결과의 맨 앞에 시간컬럼 추가
        for j in colums:
            if j == 'img_ai_img' or j == 'c': #이미지필드 따로 처리, 뒤쪽의 'c' 는 디버깅용 테이블
                t.append( np.frombuffer(getattr(row, j), dtype=np.uint8).reshape((300, 300, 3)) )
                #print('sadas',getattr(row, j)) #디버그, 주소리턴
            else:
                t.append(getattr(row, j))
                #print('sadas',getattr(row, j)) #디버그, 주소리턴
        result_list.append(t)
        t = []
        
    return result_list



def strDate_to_datetime(s_date: str):
    if len(s_date) > 12:
        return datetime.datetime.strptime(s_date,'%Y%m%d%H%M%S.%f')
    else:
        return datetime.datetime.strptime(s_date,'%Y%m%d%H%M')
    


def strBool_to_bool(s_sync: str):
    if s_sync == 'True' or s_sync == 'T' or s_sync == 'TURE' or s_sync == 't' or s_sync == '1':
        return True
    elif s_sync == 'False' or s_sync == 'F' or s_sync == 'FALSE' or s_sync == 'f' or s_sync == '0':
        return False


def strImgpath_processing(img_path: str):
    ''' img_ai_img = BlobField(null=True, default=None) 에 적용됨 '''
    img = cv.imread(img_path, cv.IMREAD_COLOR) #<class 'numpy.ndarray'> uint8
    #print(len(img), len(img[0]))
    return img.tobytes()




def count_for_value(table_, range_start, range_end, cloum, value):
    count_value = table_.select().where(
        (getattr(table_, cloum) == value) &
        (table_.daytime >= range_start) &
        (table_.daytime <= range_end)
    ).count()

    if count_value > 0:
        return True # 기록 중 해당 값 존재
    else:
        return False # 기록 중 해당 값 없음







def main(args_tuple: tuple = None):
    parser = argparse.ArgumentParser(prog=sys.argv[0], add_help=True)
    parser.add_argument('-tn', '--table_name', type=str)

    subparser = parser.add_subparsers(dest='mode', help='mode help')

    ## subparser for command 'subparser'
    # insert
    parser_insert = subparser.add_parser('insert', add_help=True)
    parser_insert.add_argument('--data', nargs='*', type=str, default=[])
    parser_insert.add_argument('--columns', nargs='*', type=str, default=[])

    # output
    parser_output = subparser.add_parser('output', add_help=True)
    parser_output.add_argument('--columns', nargs='*', action='store', type=str, default=[])
    group_output = parser_output.add_mutually_exclusive_group() ##
    group_output.add_argument('--range', nargs=2, type=str)
    group_output.add_argument('--before', action='store', type=str)
    group_output.add_argument('--after', action='store', type=str)
    group_output.add_argument('--pointer', action='store', type=str)

    # delete
    parser_delete = subparser.add_parser('delete', add_help=True)
    group_delete = parser_delete.add_mutually_exclusive_group(required=True) ##
    group_delete.add_argument('--range', nargs=2, type=str)
    group_delete.add_argument('--before', action='store', type=str)
    group_delete.add_argument('--after', action='store', type=str)
    group_delete.add_argument('--pointer', action='store', type=str)

    # update
    parser_update = subparser.add_parser('update', add_help=True)
    parser_update.add_argument('--pointer', action='store', type=str, required=True)
    parser_update.add_argument('--data', nargs='+', type=str, required=True)
    parser_update.add_argument('--columns', nargs='+', type=str, required=True)


    # 특별 기능 모드
    parser_f1_rpf = subparser.add_parser('request_past_frozen', add_help=True)
    parser_f1_rpf.add_argument('--pointer', action='store', type=str, required=True)

    parser_f2_rpr = subparser.add_parser('request_past_rain', add_help=True)
    parser_f2_rpr.add_argument('--pointer', action='store', type=str, required=True)

    parser_f3_rdst = subparser.add_parser('request_delta_surface_temperature', add_help=True)
    parser_f3_rdst.add_argument('--pointer', action='store', type=str, required=True)
    parser_f3_rdst.add_argument('--channel', type=int, default=1) # 노면온도 로거의 채널 지정


    if args_tuple == None:
        ## 명령줄 인자로 실행할 때
        args = parser.parse_args()
    else:
        ## 외부모듈에서 main을 import 로 실행할 때
        args = parser.parse_args(args = args_tuple[1:])

    ## DB 테이블의 비명시적 연결이 존재할 수 있으므로 명시적으로 관리를 시작해줘야 함
    ## https://docs.peewee-orm.com/en/latest/peewee/database.html#connection-management
    datatables.global_database.connect(reuse_if_open=True)
    table = getattr(datatables, args.table_name)

    if table == None:
        raise Exception(f'{args.table_name} 테이블이 없습니다.')

    field_ = table._meta.fields
    #print(type(field_))
    try:
        field_.pop('id')
    except:
        pass
    field_ = list(field_.keys())

    #print(field_ , type(field_))
    #print('ddd',table, table.__name__, field_)

    datatables.global_database.connect(reuse_if_open=True)

    if args.mode == 'insert':
        #args.data, args.columns
        if len(args.data) != len(args.columns):
            raise Exception(f'컬럼 수와 데이터 수가 일치하지 않습니다.\n{args.data}\n{args.columns}\n')

        data = [None] * len(field_)
        for i in range(len(field_)):
            try:
                cur = args.columns.index(field_[i]) #인자로 제공된 컬럼이 정의된 테이블의 컬럼 목록에 있을 경우
            except ValueError:
                cur = -1 #인자로 제공된 컬럼이 정의된 테이블의 컬럼 목록에 없을 경우
            
            if cur != -1:
                ### str 타입 데이터 입력을 컬럼에 따라서 알맞은 타입으로 변환

                if getattr(table, field_[i]).__class__.__name__ == 'DateTimeField':
                    data[i] = strDate_to_datetime(args.data[cur])
                elif getattr(table, field_[i]).__class__.__name__ == 'BooleanField':
                    data[i] = strBool_to_bool(args.data[cur])

                #img_ai_img = BlobField(null=True, default=None) # 입출력 시 파일의 경로(문자열)를 통해 동작함에 유의
                elif getattr(table, field_[i]).__class__.__name__ == 'BlobField':
                    data[i] = strImgpath_processing(args.data[cur])
                else:
                    data[i] = args.data[cur]
            else:
                pass
                
        data = [tuple(data)] ## 입력 형식 맞추기
    
        try: # 트랜잭션 중에 오류가 발생한 경우 롤백하여 이전 상태로 복원
            with datatables.global_database.atomic() as transaction:
                table.insert_many(data, fields=field_).execute()
                transaction.commit()

        except Exception as e:
            #transaction.rollback() #명시적 호출 필요 x
            datatables.global_database.close()
            raise Exception(f'insert 트랜잭션 실패\n{e}')
            
        datatables.global_database.close()
        return


    elif args.mode == 'output':

        try: # 트랜잭션 중에 오류가 발생한 경우 롤백하여 이전 상태로 복원, 이 경우에는 단순 조회이므로 필요성 낮음
            with datatables.global_database.atomic() as transaction:
                ## 출력 기간(범위) 지정
                if args.range:
                    form_check(args.range)
                    query = table.select().where((table.daytime >= strDate_to_datetime(args.range[0])) & (table.daytime < strDate_to_datetime(args.range[1]))).order_by(table.daytime)

                elif args.before:
                    form_check([args.before])
                    query = table.select().where(table.daytime < strDate_to_datetime(args.before)).order_by(table.daytime)

                elif args.after:
                    form_check([args.after])
                    query = table.select().where(table.daytime >= strDate_to_datetime(args.after)).order_by(table.daytime)

                elif args.pointer:
                    form_check([args.pointer])
                    query = table.select().where(table.daytime == strDate_to_datetime(args.pointer)).order_by(table.daytime)

                else:
                    query = table.select().order_by(table.daytime)
                
                transaction.commit()

        except Exception as e:
            #transaction.rollback() #명시적 호출 필요 x
            datatables.global_database.close()
            raise Exception(f'output 트랜잭션 실패\n{e}')
            
        datatables.global_database.close()


        ## 출력 컬럼 관련 제어
        if  args.columns != []:
            final_result = query_parse(query, args.columns)
        else:
            final_result = query_parse(query, field_)


        if args_tuple == None: ## 명령줄 인자로 실행할 때
            print_query_results(final_result)
            return
        else: ## 외부모듈에서 main을 import 로 실행할 때
            return final_result


    elif args.mode == 'delete':

        try: # 트랜잭션 중에 오류가 발생한 경우 롤백하여 이전 상태로 복원
            with datatables.global_database.atomic() as transaction:
                ## 삭제 기간(범위) 지정, 변수 r 에는 작업 수행시 삭제된 레코드 수가 리턴됨
                if args.range:
                    form_check(args.range)
                    r = table.delete().where( (table.daytime >= strDate_to_datetime(args.range[0])) & (table.daytime < strDate_to_datetime(args.range[1])) ).execute()

                elif args.before:
                    form_check([args.before])
                    r = table.delete().where(table.daytime < strDate_to_datetime(args.before)).execute()

                elif args.after:
                    form_check([args.after])
                    r = table.delete().where(table.daytime >= strDate_to_datetime(args.after)).execute()

                elif args.pointer:
                    form_check([args.pointer])
                    r = table.delete().where(table.daytime == strDate_to_datetime(args.pointer)).execute()

                else:
                    pass
                transaction.commit()

        except Exception as e:
            #transaction.rollback() #명시적 호출 필요 x
            datatables.global_database.close()
            raise Exception(f'delete 트랜잭션 실패\n{e}')
            
        datatables.global_database.close()
        return


    elif args.mode == 'update':
        form_check([args.pointer])

        if args.columns.__contains__(field_[0]):
            raise Exception(f'시간({field_[0]}) 컬럼은 고유 키이므로 수정이 불가능합니다.')
        if len(args.data) != len(args.columns):
            raise Exception(f'컬럼 수와 데이터 수가 일치하지 않습니다.\n{args.data}\n{args.columns}\n')
        
        #row = table.get(table.daytime == strDate_to_datetime(args.pointer))
        #print(row, type(row), row._meta.fields)

        #fields = table._meta.fields
        #fk = fields.keys()
        #fv = fields.values()

        update_data = {}
        for i in range(len(args.columns)):
            if args.columns[i] != 'img_ai_img':
                update_data[f'{args.columns[i]}'] = args.data[i]
            else:
                update_data[f'{args.columns[i]}'] = strImgpath_processing(args.data[i])

        try: # 트랜잭션 중에 오류가 발생한 경우 롤백하여 이전 상태로 복원
            with datatables.global_database.atomic() as transaction:
                ret = table.update(**update_data).where(table.daytime == strDate_to_datetime(args.pointer)).execute()
                if ret <= 0:
                    raise Exception(f'{args.pointer} 의 데이터 {table.get(table.daytime == strDate_to_datetime(args.pointer))}' + \
                            '\n 의 업데이트에 실패하였습니다.')
                transaction.commit()

        except Exception as e:
            #transaction.rollback() #명시적 호출 필요 x
            datatables.global_database.close()
            raise Exception(f'update 트랜잭션 실패 \n{e}')
            
        datatables.global_database.close()
        return


    elif args.mode == 'request_past_frozen':
        # 특정 기간 동안 'F'(빙결 상태) 값의 개수 세기(현재로부터 과거 4시간 실제 기록(예측치도 포함된))

        rpf_result = []

        if args.pointer:
            form_check(args.pointer)
            p = strDate_to_datetime(args.pointer)
            start = p + datetime.timedelta(minutes=-240)  #시작
            end = p  # 종료

        try: # 트랜잭션 중에 오류가 발생한 경우 롤백하여 이전 상태로 복원, 이 경우에는 단순 조회이므로 필요성 낮음
            with datatables.global_database.atomic() as transaction:
                query = table.select().where((table.daytime >= start) & (table.daytime < end)).order_by(table.daytime)
                transaction.commit()

        except Exception as e:
            datatables.global_database.close()
            raise Exception(f'request_past_frozen 과거기록 조회 실패\n{e}')
        datatables.global_database.close()


        result_ = query_parse(query, ['daytime', 'classifier_now_surface_state', 'classifier_1h_surface_state', 'classifier_2h_surface_state'])
        result_ = np.array(result_)

        ## 현재시간으로부터 4시간 전까지의 빙결 분류 이력 중 빙결 존재여부
        if np.count_nonzero(result_[:, [1]] == 'F') > 0:
            rpf_result.append(True)
        else:
            rpf_result.append(False)

        ## 미래시간으로부터 1시간 전까지의 빙결 분류 예측 중 빙결 존재여부,
        ## 현재시간으로부터 3시간 전까지의 빙결 분류 이력 중 빙결 존재여부
        range = result_[:, [0]] >= (p + datetime.timedelta(minutes=-60)) #1시간 전까지
        pre = np.count_nonzero(result_[:, [2]][range] == 'F') #컬럼선택(classifier_1h_surface_state), 빙결 'F' 상태 갯수
        range = result_[:, [0]] >= (p + datetime.timedelta(minutes=-180)) #3시간 전까지
        real = np.count_nonzero(result_[:, [1]][range] == 'F') #컬럼선택(classifier_now_surface_state), 빙결 'F' 상태 갯수
        if pre + real > 0:
            rpf_result.append(True)
        else:
            rpf_result.append(False)


        ## 미래1시간으로부터 1시간 전까지의 빙결 분류 예측 중 빙결 존재여부,
        ## 미래2시간으로부터 1시간 전까지의 빙결 분류 예측 중 빙결 존재여부,
        ## 현재시간으로부터 2시간 전까지의 빙결 분류 이력 중 빙결 존재여부
        range = result_[:, [0]] >= (p + datetime.timedelta(minutes=-60)) #1시간 전까지
        pre_1 = np.count_nonzero(result_[:, [2]][range] == 'F') #컬럼선택(classifier_1h_surface_state), 빙결 'F' 상태 갯수
        range = result_[:, [0]] >= (p + datetime.timedelta(minutes=-60)) #1시간 전까지
        pre_2 = np.count_nonzero(result_[:, [3]][range] == 'F') #컬럼선택(classifier_2h_surface_state), 빙결 'F' 상태 갯수
        range = result_[:, [0]] >= (p + datetime.timedelta(minutes=-120)) #2시간 전까지
        real = np.count_nonzero(result_[:, [1]][range] == 'F') #컬럼선택(classifier_now_surface_state), 빙결 'F' 상태 갯수
        if pre_1 + pre_2 + real > 0:
            rpf_result.append(True)
        else:
            rpf_result.append(False)

        
        if args_tuple == None: ## 명령줄 인자로 실행할 때
            print(*rpf_result)
            return
        else: ## 외부모듈에서 main을 import 로 실행할 때
            return rpf_result

            
    elif args.mode == 'request_pase_rain':
        rpr_result = []

        if args.pointer:
            form_check(args.pointer)
            p = strDate_to_datetime(args.pointer)
            start = p + datetime.timedelta(minutes=-180)  #시작
            end = p  # 종료

        try: # 트랜잭션 중에 오류가 발생한 경우 롤백하여 이전 상태로 복원, 이 경우에는 단순 조회이므로 필요성 낮음
            with datatables.global_database.atomic() as transaction:
                query = table.select().where((table.daytime >= start) & (table.daytime < end)).order_by(table.daytime)
                transaction.commit()

        except Exception as e:
            datatables.global_database.close()
            raise Exception(f'request_pase_rain 과거기록 조회 실패\n{e}')
        datatables.global_database.close()


        ### 현재는 엣지 디바이스의 과거 날씨 분류 이력만을 사용하고 있으나, 
        ### 추후 기상청 API정보를 고려하는 등의 추가구현 있을 수 있음
        result_ = query_parse(query, ['daytime', 'weather', 'ai1h_out_weather', 'ai2h_out_weather'])
        result_ = np.array(result_)


        ## 현재시간으로부터 3시간 전까지의 날씨 이력 중 강수 존재여부
        if np.count_nonzero(result_[:, [1]] == 'R') > 0:
            rpr_result.append(True)
        else:
            rpr_result.append(False)


        ## 미래시간으로부터 1시간 전까지의 날씨 예측 중 강수 존재여부,
        ## 현재시간으로부터 2시간 전까지의 날씨 이력 중 강수 존재여부
        range = result_[:, [0]] >= (p + datetime.timedelta(minutes=-60)) #1시간 전까지
        pre = np.count_nonzero(result_[:, [2]][range] == 'R') #컬럼선택(ai1h_out_weather), 강수 'R' 상태 갯수
        range = result_[:, [0]] >= (p + datetime.timedelta(minutes=-120)) #2시간 전까지
        real = np.count_nonzero(result_[:, [1]][range] == 'R') #컬럼선택(weather), 강수 'R' 상태 갯수
        if pre + real > 0:
            rpr_result.append(True)
        else:
            rpr_result.append(False)


        ## 미래1시간으로부터 1시간 전까지의 날씨 예측 중 강수 존재여부,
        ## 미래2시간으로부터 1시간 전까지의 날씨 예측 중 강수 존재여부,
        ## 현재시간으로부터 1시간 전까지의 빙결 분류 이력 중 빙결 존재여부
        range = result_[:, [0]] >= (p + datetime.timedelta(minutes=-60)) #1시간 전까지
        pre_1 = np.count_nonzero(result_[:, [2]][range] == 'R') #컬럼선택(ai1h_out_weather), 강수 'R' 상태 갯수
        range = result_[:, [0]] >= (p + datetime.timedelta(minutes=-60)) #1시간 전까지
        pre_2 = np.count_nonzero(result_[:, [3]][range] == 'R') #컬럼선택(ai2h_out_weather), 강수 'R' 상태 갯수
        range = result_[:, [0]] >= (p + datetime.timedelta(minutes=-60)) #1시간 전까지
        real = np.count_nonzero(result_[:, [1]][range] == 'R') #컬럼선택(weather), 강수 'R' 상태 갯수
        if pre_1 + pre_2 + real > 0:
            rpr_result.append(True)
        else:
            rpr_result.append(False)


        if args_tuple == None: ## 명령줄 인자로 실행할 때
            print(*rpr_result)
            return
        else: ## 외부모듈에서 main을 import 로 실행할 때
            return rpr_result
        


    elif args.mode == 'request_delta_surface_temperature':
        rdst_result = []

        if args.pointer:
            form_check(args.pointer)
            p = strDate_to_datetime(args.pointer)
            start = p + datetime.timedelta(minutes=-2)  #시작
            end = p  # 종료

            past_start = start + datetime.timedelta(minutes=-62)  #시작
            past_end = p + datetime.timedelta(minutes=-58)  #종료

        try: # 트랜잭션 중에 오류가 발생한 경우 롤백하여 이전 상태로 복원, 이 경우에는 단순 조회이므로 필요성 낮음
            with datatables.global_database.atomic() as transaction:
                query = table.select().where((table.daytime >= start) & (table.daytime < end)).order_by(table.daytime)
                query_p = table.select().where((table.daytime >= past_start) & (table.daytime < past_end)).order_by(table.daytime)
                transaction.commit()

        except Exception as e:
            datatables.global_database.close()
            raise Exception(f'request_delta_surface_temperature 조회 실패\n{e}')
        datatables.global_database.close()

        result_ = query_parse(query, [f'surface_ch{args.channel}', 'ai1h_out_surface_temperature', 'ai2h_out_surface_temperature'])
        result_ = np.array(result_)
        result_p = query_parse(query_p, [f'surface_ch{args.channel}', 'ai1h_out_surface_temperature', 'ai2h_out_surface_temperature'])
        result_p = np.array(result_p)


        ## 현재시간의 시간당 노면온도 변화량(현재 실측 온도 - 1시간 전 실측온도)
        real = result_[:, [0]].reshape( len(result_) )[-1]

        if len(result_p) < 5: #1시간 전 실측온도 윈도우 중 결측치가 있다면 주변값의 평균으로 대체
            past_real = sum( result_p[:, [0]].reshape(len(result_p)) ) / len(result_p)
        else: # 결측치가 없다면 중앙값(해당 시간의 측정치)
            past_real = result_p[:, [0]].reshape(len(result_p))[1]
        
        rdst_result.append(real - past_real)

        ## 1시간후 미래의 시간당 노면온도 변화량(1시간후 예측 온도 - 현재 실측 온도)
        pre_1h = result_[:, [1]].reshape( len(result_) )[-1]
        rdst_result.append(pre_1h - real)

        ## 2시간후 미래의 시간당 노면온도 변화량(2시간 후 예측 온도 - 1시간후 예측 온도)
        pre_2h = result_[:, [2]].reshape( len(result_) )[-1]
        rdst_result.append(pre_2h - pre_1h)


        if args_tuple == None: ## 명령줄 인자로 실행할 때
            print(*rdst_result)
            return
        else: ## 외부모듈에서 main을 import 로 실행할 때
            return rdst_result


    else:
        datatables.global_database.close()
        raise Exception(f'동작이 명확히 지정되지 않았습니다.')





if __name__ =="__main__":
    try:
        main()
        sys.exit(0)

    except peewee.OperationalError as e:
        print(f'{__file__} :\n데이터베이스 오류 \n{e}', file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f'{__file__} :\n {e}', file=sys.stderr)
        sys.exit(1)





'''
TEST INPUTS


INSERT
python database_iod.py -tn UNIONTABLE insert --data F 202311061200 --columns server_synchronize daytime
python database_iod.py -tn UNIONTABLE insert --data F 202311051911 --columns server_synchronize daytime
python database_iod.py -tn UNIONTABLE insert --data F 202311061200 33 --columns server_synchronize daytime api_wind_velocity



OUTPUT
python database_iod.py -tn UNIONTABLE output
python database_iod.py -tn UNIONTABLE output --pointer 202311061200
python database_iod.py -tn UNIONTABLE output --pointer 202311061200 --columns daytime
python database_iod.py -tn UNIONTABLE output --pointer 202311061200 --columns server_synchronize daytime
python database_iod.py -tn UNIONTABLE output --after 202311061200
python database_iod.py -tn UNIONTABLE output --after 202311061200 --columns daytime
python database_iod.py -tn UNIONTABLE output --after 202311061200 --columns server_synchronize daytime
python database_iod.py -tn UNIONTABLE output --before 202311061200
python database_iod.py -tn UNIONTABLE output --before 202311061200 --columns daytime
python database_iod.py -tn UNIONTABLE output --before 202311061200 --columns server_synchronize daytime
python database_iod.py -tn UNIONTABLE output --range 202311061100 202311061300
python database_iod.py -tn UNIONTABLE output --range 202311061100 202311061300 --columns daytime
python database_iod.py -tn UNIONTABLE output --range 202311061100 202311061300 --columns server_synchronize daytime


DELETE
python database_iod.py -tn UNIONTABLE delete --pointer 202311061200
python database_iod.py -tn UNIONTABLE delete --after 202311061200
python database_iod.py -tn UNIONTABLE delete --before 202311061200
python database_iod.py -tn UNIONTABLE delete --range 202311061100 202311061300



UPDATE
python database_iod2.py -tn UNIONTABLE update --pointer 202311051911 --columns api_air_temperature api_wind_velocity --data 20 10
'''
