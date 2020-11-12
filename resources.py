from datetime import datetime, timedelta
import pandas as pd
import numpy as np


class CustomException(Exception):
    pass


class LinkEvents:

    def __init__(self, incomes, outcomes, days=30, order='montoTotal'):
        self.incomes = self.order_events(incomes, order)
        self.outcomes = self.order_events(outcomes, order)
        self.days = days


    @staticmethod
    def filter_on_date(date, outcomes, days):
        base_date = datetime.strptime(date, "%d-%m-%Y")
        range_date = [base_date - timedelta(days=day) for day in range(days)]
        outcomes_filtered = [outcome for outcome in outcomes if datetime.strptime(outcome['fechaDeOperacion'], "%d-%m-%Y") in range_date]
        return outcomes_filtered


    @staticmethod
    def order_events(events, order):
        df = pd.DataFrame(events)
        df['fechaDeOperacion'] = pd.to_datetime(df['fechaDeOperacion'], format="%d-%m-%Y")
        df = df.sort_values(by=order)
        df['fechaDeOperacion'] = df['fechaDeOperacion'].dt.strftime("%d-%m-%Y")
        new_order = []
        for index, row in df.iterrows():
            dic = {
                'montoTotal': row['montoTotal'],
                'fechaDeOperacion': row['fechaDeOperacion'],
                'id': row['id']
            }
            new_order.append(dic)
        return new_order
    

    def link_by_outcome(self):
        linked = dict()
        for income in self.incomes:
            outcomes = self.filter_on_date(income['fechaDeOperacion'],self.outcomes,self.days)
            income_amount = income['montoTotal']
            outcome_amount = 0
            posible_linked = list()
            for outcome in outcomes:
                outcome_amount += outcome['montoTotal']
                posible_linked.append(outcome)
                if outcome_amount == income_amount:
                    linked.update({income['id']:posible_linked})
                    outcomes = [outcome for outcome in outcomes if outcome not in posible_linked]
                    self.incomes.remove(income)
                    outcome_amount = 0
                    posible_linked = list()
                    break
                elif outcome_amount < income_amount:
                    continue
                else:
                    outcome_amount = 0
                    posible_linked = list()
        
        return linked

    
    def link_by_income(self):
        linked = dict()
        for outcome in self.outcomes:
            outcome_amount = outcome['montoTotal']
            income_amount = 0
            posible_linked = list()
            for income in self.incomes:
                outcomes_dates = self.filter_on_date(income['fechaDeOperacion'],self.outcomes,self.days)
                outcome_amount = outcome['montoTotal']
                income_amount += income['montoTotal']
                posible_linked.append(income)
                if income_amount == outcome_amount:
                    linked.update({outcome['id']:posible_linked})
                    self.incomes = [income for income in self.incomes if income not in posible_linked]
                    self.outcomes.remove(outcome)
                    income_amount = 0
                    posible_linked = list()
                    break
                elif income_amount < outcome_amount:
                    continue
                else:
                    income_amount = 0
                    posible_linked = list()
        
        return linked


    def exec_mix(self, criteria):
        
        EXECS = {
            '0' : self.link_by_income,
            '1' : self.link_by_outcome,
            '2' : self.link_by_outcome
        }

        for cr in criteria:
            if cr == '2':
                outcomes = self.outcomes
                self.outcomes = self.order_events(outcomes, 'fechaDeOperacion')
            func = EXECS[cr]
            linked = func()
        return linked
