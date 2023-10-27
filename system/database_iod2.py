import sys
import peewee
import argparse
import traceback
import datetime
from typing import List

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
    입력받은 데이터에서 시간컬럼과 지정한 컬럼들을 선택함, 순서는 입력받은 컬럼명 대로
    지정한 컬럼명이 없을 시 오류
    '''
    result_list = []
    t = []
    for row in query:
        t.append(getattr(row, 'daytime'))
        for j in colums:
            t.append(getattr(row, j))
        result_list.append(t)

    return result_list



def strDate_to_datetime(s_date: str):
    return datetime.datetime.strptime(s_date,'%Y%m%d%H%M')





if __name__ =="__main__":
    try:
        parser = argparse.ArgumentParser(prog=sys.argv[0], add_help=True)
        parser.add_argument('-tn', '--table_name', type=str)

        subparser = parser.add_subparsers(dest='mode', help='mode help')

        ## subparser for command 'subparser'
        # insert
        parser_insert = subparser.add_parser('insert', add_help=True)
        parser_insert.add_argument('--data', nargs='*', type=str)
        parser_insert.add_argument('--columns', nargs='*', type=str)

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

        args = parser.parse_args()




        table = getattr(datatables, args.table_name)
        if table == None:
            raise Exception(f'{args.table_name} 테이블이 없습니다.')

        field_ = table._meta.fields
        field_.pop('id')
        field_ = list(field_.keys())

        #print(field_ , type(field_))
        #print('ddd',table, table.__name__, field_)


        if args.mode == 'insert':
            #args.data, args.columns
            if len(args.data) != len(args.columns):
                raise Exception(f'컬럼 수와 데이터 수가 일치하지 않습니다.\n{args.data}\n{args.columns}\n')

            data = []
            for i in range(len(field_)):
                if args.columns.__contains__(field_[i]):
                    data.append(args.data[i])
                else:
                    data.append(None)

            data = [tuple(data)] ## 입력 형식 맞추기
            # data 내부에 None 이 있다면 None 타입이 아닌 'None' 로 입력될 수 있음. 확인필요
            datatables.global_database.connect()
            table.insert_many(data, fields=field_).execute()
            datatables.global_database.close()
            #print('--insert')
            sys.exit(0)


        elif args.mode == 'output':

            ## 출력 기간 관련 제어
            if args.range:
                form_check(args.range)
                datatables.global_database.connect()
                query = table.select().where((table.daytime >= strDate_to_datetime(args.range[0])) & (table.daytime < strDate_to_datetime(args.range[1]))).order_by(table.daytime)
                datatables.global_database.close()

            elif args.before:
                form_check([args.before])
                datatables.global_database.connect()
                query = table.select().where(table.daytime < strDate_to_datetime(args.before)).order_by(table.daytime)
                datatables.global_database.close()

            elif args.after:
                form_check([args.after])
                datatables.global_database.connect()
                query = table.select().where(table.daytime >= strDate_to_datetime(args.after)).order_by(table.daytime)
                datatables.global_database.close()

            elif args.pointer:
                form_check([args.pointer])
                datatables.global_database.connect()
                query = table.select().where(table.daytime == strDate_to_datetime(args.pointer)).order_by(table.daytime)
                datatables.global_database.close()

            else:
                datatables.global_database.connect()
                query = table.select().order_by(table.daytime)
                datatables.global_database.close()

            ## 출력 컬럼 관련 제어
            if  args.columns != []:
                final_result = query_parse(query, args.columns)
                print_query_results(final_result)
            else:
                print_query_results(query)
            
            #print('--output')
            sys.exit(0)


        elif args.mode == 'delete':
            if args.range:
                form_check(args.range)
                datatables.global_database.connect()
                r = table.delete().where( (table.daytime >= strDate_to_datetime(args.range[0])) & (table.daytime < strDate_to_datetime(args.range[1])) ).execute()
                datatables.global_database.close()
                #print(f'{args.table_name} 테이블의 {args.range} 범위 데이터 {r} 개 삭제됨.')

            elif args.before:
                form_check([args.before])
                datatables.global_database.connect()
                r = table.delete().where(table.daytime < strDate_to_datetime(args.before)).execute()
                datatables.global_database.close()
                #print(f'{args.table_name} 테이블의 {args.before} 이전의 데이터 {r} 개 삭제됨.')

            elif args.after:
                form_check([args.after])
                datatables.global_database.connect()
                r = table.delete().where(table.daytime >= strDate_to_datetime(args.after)).execute()
                datatables.global_database.close()
                #print(f'{args.table_name} 테이블의 {args.after} 이후의 데이터 {r} 개 삭제됨.')

            elif args.pointer:
                form_check([args.pointer])
                datatables.global_database.connect()
                r = table.delete().where(table.daytime == strDate_to_datetime(args.pointer)).execute()
                datatables.global_database.close()
                #print(f'{args.table_name} 테이블의 {args.pointer} 의 단일 데이터 삭제됨.')

            else:
                pass
            sys.exit(0)


        elif args.mode == 'update':
            form_check([args.pointer])
            #args.data, args.colums

            if args.columns.__contains__(field_[0]):
                raise Exception(f'시간({field_[0]}) 컬럼은 고유 키이므로 수정이 불가능합니다.')
            if len(args.data) != len(args.columns):
                raise Exception(f'컬럼 수와 데이터 수가 일치하지 않습니다.\n{args.data}\n{args.columns}\n')
            
            row = table.get(table.name == strDate_to_datetime(args.pointer))
            rrow = row
            for i in range(len(args.columns)):
                tmp = getattr(row, args.columns[i])
                tmp = args.data[i]
            row.save()
            #print(f'기존 데이터 수정 \n원본 ㄱ\n{rrow}\n\n수정ㄱ\n{row}\n')
            sys.exit(0)


        else:
            raise Exception(f'동작이 명확히 지정되지 않았습니다.')


    except peewee.OperationalError as e:
        print(f'데이터베이스 오류 \n{e}', file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f'{e}', file=sys.stderr)
        sys.exit(1)

    #except:
    #    print(traceback.print_exc(), file=sys.stderr)
    #    if sys.stderr:
    #        sys.stderr.flush()
    #    sys.exit(1)




'''
TEST INPUTS


INSERT
python database_iod.py 



OUTPUT
python database_iod.py -tn TTable -o
python database_iod.py -tn TTable -o


DELETE
python database_iod.py -tn TTable -d pointer 1111
python database_iod.py -tn TTable -d after 1111
python database_iod.py -tn TTable -d before 1111
python database_iod.py -tn TTable -d range 1000 2023


UPDATE
python database_iod.py -tn TTable -u pointer 1111 data 1 3.14 colums b c
'''