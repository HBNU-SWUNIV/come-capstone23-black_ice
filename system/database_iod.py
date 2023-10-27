import sys
import inspect
import peewee
import argparse
from decimal import Decimal
import traceback

import datatables
from _utils import form_check




def print_dict_formatted(dict_format_data):
    formatted_data = []
    for key, value in dict_format_data.items():
        formatted_data.append(f'{key}: {value}')
    result = ', '.join(formatted_data)
    return result



def print_query_results(query):
    result_list = []
    for row in query:
        original_list = inspect.getmembers(row)
        filtered_list = [item for item in original_list if item[0] == '__data__']
        d = filtered_list[0][1]
        d.pop('id')

        for key, value in d.items():
            if isinstance(value, Decimal):
                d[key] = float(value)

        result = print_dict_formatted(d)
        result_list.append(result)
    
    if result_list == []:
        print(result_list)
    else:
        for i in result_list:
            print(i)




if __name__ =="__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-tn', '--table_name', type=str, required=True)

        parser.add_argument('-i', '--insert', action='store_true', default=False)
        parser.add_argument('-o', '--output', action='store_true', default=False)
        parser.add_argument('-d', '--delete', action='store_true', default=False)

        parser.add_argument('-ds', '--datas', nargs='*', type=str)
        parser.add_argument('-cn', '--column_names', nargs='*', type=str) ## 추가 기능(미완)
        args = parser.parse_args()



        #models = get_models(datatables)
        table = getattr(datatables, args.table_name)
        if table == None:
            raise Exception(f'{args.table_name} 테이블이 없습니다.')

        field_ = table._meta.fields
        field_.pop('id')
        field_ = list(field_.keys())
        #print(field_ , type(field_))

    
        #print('ddd',table, table.__name__, field_)

        if args.insert:
            if args.output or args.delete:
                raise Exception(f'동작이 명확히 지정되지 않았습니다.')
            
            if args.datas:
                data = tuple(args.datas)
                data = [data]

            if len(data[0]) != len(field_):
                raise Exception(f'string argv err : 요구 인자 수( {len(field_)} ) 불일치 ( {len(data[0])} )')
            
            datatables.global_database.connect()
            # data 내부에 None 이 있다면 None 타입이 아닌 'None' 로 입력될 수 있음. 확인필요
            table.insert_many(data, fields=field_).execute()
            datatables.global_database.close()
            
            '''
            print_str = ''
            for i in range(len(field_)):
                print_str = print_str + f'  {field_[i]} : {data[0][i]}\n'
            print(f'SAVE -> {args.table_name}')
            print(print_str)
            '''
            sys.exit(0)

        elif args.output:
            if args.insert or args.delete:
                raise Exception(f'동작이 명확히 지정되지 않았습니다.')
            
            if not args.datas:
                datatables.global_database.connect()
                query = table.select().order_by(table.daytime)
                datatables.global_database.close()
                print_query_results(query)
                sys.exit(0)
            

            if args.datas[0] == 'range':
                if len(args.datas) <= 2:
                    raise Exception(f'시간 범위를 입력해 주십시오')
                
                if len(args.datas) >= 4:
                    print(f'입력 무시됨 ({args.datas[3:]})')

                start = args.datas[1]
                end = args.datas[2]
                form_check([start, end])
                
                datatables.global_database.connect()
                query = table.select().where((table.daytime >= start) & (table.daytime < end)).order_by(table.daytime)
                datatables.global_database.close()
                
            elif args.datas[0] == 'before':
                if len(args.datas) <= 1:
                    raise Exception(f'시간 범위를 입력해 주십시오')
                form_check([args.datas[1]])
                
                datatables.global_database.connect()
                query = table.select().where(table.daytime < args.datas[1]).order_by(table.daytime)
                datatables.global_database.close()

            elif args.datas[0] == 'after':
                if len(args.datas) <= 1:
                    raise Exception(f'시간 범위를 입력해 주십시오')
                form_check([args.datas[1]])
                
                datatables.global_database.connect()
                query = table.select().where(table.daytime >= args.datas[1]).order_by(table.daytime)
                datatables.global_database.close()

            elif args.datas[0] == 'point':
                if len(args.datas) <= 1:
                    raise Exception(f'시간을 입력해 주십시오')
                form_check([args.datas[1]])
                
                datatables.global_database.connect()
                query = table.select().where(table.daytime == args.datas[1]).order_by(table.daytime)
                datatables.global_database.close()
                
            else:
                raise Exception(f'동작이 명확히 지정되지 않았습니다.')
            
            print_query_results(query)
            sys.exit(0)
            
        elif args.delete:
            if args.insert or args.output or (not args.datas):
                raise Exception(f'동작이 명확히 지정되지 않았습니다.')
            
            
            if args.datas[0] == 'range':
                if len(args.datas) <= 2:
                    raise Exception(f'시간 범위를 입력해 주십시오')
                
                if len(args.datas) >= 4:
                    print(f'입력 무시됨 ({args.datas[3:]})')

                start = args.datas[1]
                end = args.datas[2]
                form_check([start, end])
                
                datatables.global_database.connect()
                r = table.delete().where( (table.daytime >= start) & (table.daytime < end) ).execute()
                datatables.global_database.close()
                #print(f'{args.table_name} 에서  {start} ~ {end} 범위의 데이터 {r}개 삭제됨.')
                sys.exit(0)

            elif args.datas[0] == 'before':
                if len(args.datas) <= 1:
                    raise Exception(f'시간 범위를 입력해 주십시오')
                form_check([args.datas[1]])
                
                datatables.global_database.connect()
                r = table.delete().where(table.daytime < args.datas[1]).execute()
                datatables.global_database.close()
                #print(f'{args.table_name} 에서  {args.datas[1]}이전의 데이터 {r}개 삭제됨.')
                sys.exit(0)

            elif args.datas[0] == 'after':
                if len(args.datas) <= 1:
                    raise Exception(f'시간 범위를 입력해 주십시오')
                form_check([args.datas[1]])
                
                datatables.global_database.connect()
                r = table.delete().where(table.daytime >= args.datas[1]).execute()
                datatables.global_database.close()
                #print(f'{args.table_name} 에서  {args.datas[1]}이후의 데이터 {r}개 삭제됨.')
                sys.exit(0)

            elif args.datas[0] == 'point':
                if len(args.datas) <= 1:
                    raise Exception(f'시간을 입력해 주십시오')
                form_check([args.datas[1]])
                
                datatables.global_database.connect()
                r = table.delete().where(table.daytime == args.datas[1]).execute()
                datatables.global_database.close()
                #print(f'{args.table_name} 에서 daytime = {args.datas[1]}인 데이터 {r}개 삭제됨.')
                sys.exit(0)
            else:
                raise Exception(f'동작이 명확히 지정되지 않았습니다.')
            
        #elif:
            

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
TEST


insert
python database_iod.py -i -tn TTable -ds 202309200010 2 3 4 5 7 8 9 6
python database_iod.py -i -tn TTable -ds 202309200011 2 3 4 5 7 8 9 6
python database_iod.py -i -tn TTable -ds 102309200010 2 3 4 5 7 8 9 6
python database_iod.py -tn TTable -i -ds 1111 1 32 3 4 5 6 7 8 9 # err
python database_iod.py -tn TTable -i -ds 1111 1 32 3 4 5 a 7 8 #err 


output 
python database_iod.py -tn TTable -o -ds point 1111
python database_iod.py -tn TTable -o -ds point 102309200010
python database_iod.py -tn TTable -o -ds point 202309200011
python database_iod.py -tn TTable -o -ds point 202309200010
python database_iod.py -tn TTable -o -ds after 1111
python database_iod.py -tn TTable -o -ds after 102309200010
python database_iod.py -tn TTable -o -ds after 202309200011
python database_iod.py -tn TTable -o -ds after 202309200010
python database_iod.py -tn TTable -o -ds before 1111
python database_iod.py -tn TTable -o -ds before 102309200010
python database_iod.py -tn TTable -o -ds before 202309200011
python database_iod.py -tn TTable -o -ds before 202309200010
python database_iod.py -tn TTable -o -ds point 1111
python database_iod.py -tn TTable -o -ds point 102309200010
python database_iod.py -tn TTable -o -ds point 202309200011
python database_iod.py -tn TTable -o -ds point 202309200010
python database_iod.py -tn TTable -o -ds range 1000 2023
python database_iod.py -tn TTable -o -ds range 100.0 2023
python database_iod.py -tn TTable -o -ds range 10.00 2023
python database_iod.py -tn TTable -o -ds range 10.00. 202n #err
python database_iod.py -tn TTable -o -ds range 10.00 202 saf dsj #입력 무시됨 (['saf', 'dsj'])
python database_iod.py -tn TTable -o


delete
python database_iod.py -tn TTable -d -ds point 1111
python database_iod.py -tn TTable -d -ds point 102309200010
python database_iod.py -tn TTable -d -ds point 202309200011
python database_iod.py -tn TTable -d -ds point 202309200010
python database_iod.py -tn TTable -d -ds after 1111
python database_iod.py -tn TTable -d -ds after 102309200010
python database_iod.py -tn TTable -d -ds after 202309200011
python database_iod.py -tn TTable -d -ds after 202309200010
python database_iod.py -tn TTable -d -ds before 1111
python database_iod.py -tn TTable -d -ds before 102309200010
python database_iod.py -tn TTable -d -ds before 202309200011
python database_iod.py -tn TTable -d -ds before 202309200010
python database_iod.py -tn TTable -d -ds point 1111
python database_iod.py -tn TTable -d -ds point 102309200010
python database_iod.py -tn TTable -d -ds point 202309200011
python database_iod.py -tn TTable -d -ds point 202309200010
python database_iod.py -tn TTable -d -ds range 1000 2023
python database_iod.py -tn TTable -d -ds range 100.0 2023
python database_iod.py -tn TTable -d -ds range 10.00 2023
python database_iod.py -tn TTable -d -ds range 10.00. 20a3 #err
python database_iod.py -tn TTable -d -ds range 10.00 202 saf dsj #입력 무시됨 (['saf', 'dsj'])
python database_iod.py -tn TTable -d


'''
