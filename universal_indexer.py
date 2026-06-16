#!/usr/bin/env python3
"""
Universal AI-Powered Smart Contract Indexer & Chatbot
Hardcoded configuration - Just the chatbot CLI
"""

import json
import time
import re
import sqlite3
from web3 import Web3
from web3.middleware import geth_poa_middleware
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import hashlib
import os
import sys
import readline
from colorama import init, Fore, Style, Back

# Initialize colorama for colored output
init(autoreset=True)

# ============================================
# HARDCODED CONFIGURATION - CHANGE THESE!
# ============================================

# ===== BLOCKCHAIN CONFIGURATION =====
CONTRACT_ADDRESS = "0x99D690a96377238633cEA9262944bd0F2f9CaAd4"  # ← CHANGE THIS
RPC_URL = "https://sepolia.drpc.org"  # Change for different chains

# ===== AI CONFIGURATION =====
OLLAMA_URL = "http://localhost:11434/api/generate"
LLM_MODEL = "llama3.2:3b"

# ===== DATABASE =====
DB_FILE = "contract_indexer.db"

# ============================================
# HARDCODED ABI - REPLACE WITH YOUR CONTRACT ABI
# ============================================

CONTRACT_ABI = [
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "spender",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "value",
        "type": "uint256"
      }
    ],
    "name": "approve",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "uint256",
        "name": "value",
        "type": "uint256"
      }
    ],
    "name": "burn",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "account",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "value",
        "type": "uint256"
      }
    ],
    "name": "burnFrom",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "recipient",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "initialOwner",
        "type": "address"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "constructor"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "spender",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "allowance",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "needed",
        "type": "uint256"
      }
    ],
    "name": "ERC20InsufficientAllowance",
    "type": "error"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "sender",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "balance",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "needed",
        "type": "uint256"
      }
    ],
    "name": "ERC20InsufficientBalance",
    "type": "error"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "approver",
        "type": "address"
      }
    ],
    "name": "ERC20InvalidApprover",
    "type": "error"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "receiver",
        "type": "address"
      }
    ],
    "name": "ERC20InvalidReceiver",
    "type": "error"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "sender",
        "type": "address"
      }
    ],
    "name": "ERC20InvalidSender",
    "type": "error"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "spender",
        "type": "address"
      }
    ],
    "name": "ERC20InvalidSpender",
    "type": "error"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "owner",
        "type": "address"
      }
    ],
    "name": "OwnableInvalidOwner",
    "type": "error"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "account",
        "type": "address"
      }
    ],
    "name": "OwnableUnauthorizedAccount",
    "type": "error"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": True,
        "internalType": "address",
        "name": "owner",
        "type": "address"
      },
      {
        "indexed": True,
        "internalType": "address",
        "name": "spender",
        "type": "address"
      },
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "value",
        "type": "uint256"
      }
    ],
    "name": "Approval",
    "type": "event"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "to",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "mint",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": True,
        "internalType": "address",
        "name": "previousOwner",
        "type": "address"
      },
      {
        "indexed": True,
        "internalType": "address",
        "name": "newOwner",
        "type": "address"
      }
    ],
    "name": "OwnershipTransferred",
    "type": "event"
  },
  {
    "inputs": [],
    "name": "renounceOwnership",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "to",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "value",
        "type": "uint256"
      }
    ],
    "name": "transfer",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": True,
        "internalType": "address",
        "name": "from",
        "type": "address"
      },
      {
        "indexed": True,
        "internalType": "address",
        "name": "to",
        "type": "address"
      },
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "value",
        "type": "uint256"
      }
    ],
    "name": "Transfer",
    "type": "event"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "from",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "to",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "value",
        "type": "uint256"
      }
    ],
    "name": "transferFrom",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "newOwner",
        "type": "address"
      }
    ],
    "name": "transferOwnership",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "owner",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "spender",
        "type": "address"
      }
    ],
    "name": "allowance",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "account",
        "type": "address"
      }
    ],
    "name": "balanceOf",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "decimals",
    "outputs": [
      {
        "internalType": "uint8",
        "name": "",
        "type": "uint8"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "name",
    "outputs": [
      {
        "internalType": "string",
        "name": "",
        "type": "string"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "owner",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "symbol",
    "outputs": [
      {
        "internalType": "string",
        "name": "",
        "type": "string"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "totalSupply",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  }
]

# ============================================
# DATABASE MANAGER
# ============================================

class DatabaseManager:
    """Manages SQLite database operations"""
    
    def __init__(self, db_file: str):
        self.db_file = db_file
        self.connection = None
        self.connect()
    
    def connect(self):
        """Connect to SQLite database"""
        try:
            self.connection = sqlite3.connect(self.db_file)
            self.connection.row_factory = sqlite3.Row
            print(f"{Fore.GREEN}✅ Connected to SQLite database: {self.db_file}{Style.RESET_ALL}")
            self.execute("PRAGMA foreign_keys = ON")
        except Exception as e:
            print(f"{Fore.RED}❌ Failed to connect to SQLite: {e}{Style.RESET_ALL}")
            sys.exit(1)
    
    def execute(self, query: str, params: tuple = None):
        """Execute a query and return results"""
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                cursor.close()
                return [dict(row) for row in results]
            else:
                self.connection.commit()
                cursor.close()
                return cursor.rowcount
        except Exception as e:
            self.connection.rollback()
            cursor.close()
            raise e
    
    def create_tables(self, contract_address: str, abi: List[Dict]):
        """Create database tables based on contract ABI"""
        print(f"\n{Fore.CYAN}📊 Creating database schema...{Style.RESET_ALL}")
        
        # Create contracts table
        self.execute("""
            CREATE TABLE IF NOT EXISTS contracts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contract_address TEXT UNIQUE NOT NULL,
                contract_name TEXT,
                abi TEXT,
                events TEXT,
                view_functions TEXT,
                last_synced_block INTEGER DEFAULT 0,
                total_events INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create event tables
        events = [item for item in abi if item.get('type') == 'event']
        
        for event in events:
            event_name = event['name']
            table_name = f"event_{event_name.lower()}"
            
            columns = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]
            
            for input_param in event.get('inputs', []):
                param_name = input_param.get('name', 'param')
                param_type = input_param.get('type', 'string')
                sqlite_type = self._solidity_to_sqlite(param_type)
                columns.append(f"{param_name} {sqlite_type}")
            
            columns.append("block_number INTEGER")
            columns.append("tx_hash TEXT")
            columns.append("created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            
            create_sql = f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    {', '.join(columns)}
                )
            """
            
            index_sql = f"""
                CREATE INDEX IF NOT EXISTS idx_{table_name}_block 
                ON {table_name} (block_number)
            """
            
            try:
                self.execute(create_sql)
                self.execute(index_sql)
                print(f"{Fore.GREEN}  ✅ Created table: {table_name}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.YELLOW}  ⚠️ Table {table_name} already exists{Style.RESET_ALL}")
        
        # Create query cache table
        self.execute("""
            CREATE TABLE IF NOT EXISTS query_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contract_address TEXT,
                query_hash TEXT UNIQUE,
                query TEXT,
                result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
        """)
        
        self.execute("""
            CREATE INDEX IF NOT EXISTS idx_query_hash 
            ON query_cache (query_hash)
        """)
        
        # Store contract metadata
        self.execute("""
            INSERT OR REPLACE INTO contracts 
            (contract_address, contract_name, abi, events, view_functions, last_synced_block)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            contract_address,
            f"Contract_{contract_address[:10]}",
            json.dumps(abi),
            json.dumps(events),
            json.dumps([f for f in abi if f.get('type') == 'function' and f.get('stateMutability') in ['view', 'pure']]),
            0
        ))
        
        print(f"{Fore.GREEN}✅ Database schema ready!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}📁 Database file: {self.db_file}{Style.RESET_ALL}")
    
    def _solidity_to_sqlite(self, solidity_type: str) -> str:
        """Convert Solidity type to SQLite type"""
        type_map = {
            'address': 'TEXT',
            'string': 'TEXT',
            'bytes': 'TEXT',
            'bool': 'INTEGER',
            'uint': 'INTEGER',
            'uint8': 'INTEGER',
            'uint16': 'INTEGER',
            'uint32': 'INTEGER',
            'uint64': 'INTEGER',
            'uint256': 'INTEGER',
            'int': 'INTEGER',
            'int8': 'INTEGER',
            'int16': 'INTEGER',
            'int32': 'INTEGER',
            'int64': 'INTEGER',
            'int256': 'INTEGER',
        }
        
        if solidity_type.endswith('[]'):
            return 'TEXT'
        
        for key in type_map:
            if solidity_type.startswith(key):
                return type_map[key]
        
        return 'TEXT'
    
    def store_event(self, contract_address: str, event_name: str, event_data):
        """Store an event in the database"""
        try:
            args = dict(event_data.args)
            table_name = f"event_{event_name.lower()}"
            
            columns = []
            values = []
            placeholders = []
            
            for key, value in args.items():
                columns.append(key)
                if isinstance(value, (list, tuple, dict)):
                    values.append(json.dumps(value))
                else:
                    values.append(value)
                placeholders.append('?')
            
            columns.extend(['block_number', 'tx_hash'])
            values.extend([event_data.blockNumber, event_data.transactionHash.hex()])
            placeholders.extend(['?', '?'])
            
            insert_sql = f"""
                INSERT INTO {table_name} ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
            """
            
            self.execute(insert_sql, tuple(values))
            
            self.execute("""
                UPDATE contracts 
                SET total_events = total_events + 1
                WHERE contract_address = ?
            """, (contract_address,))
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error storing event {event_name}: {e}{Style.RESET_ALL}")
    
    def get_cached_query(self, contract_address: str, query: str) -> Optional[Dict]:
        """Get cached query result"""
        query_hash = hashlib.md5(f"{contract_address}_{query}".encode()).hexdigest()
        
        results = self.execute("""
            SELECT result FROM query_cache 
            WHERE query_hash = ? AND expires_at > datetime('now')
        """, (query_hash,))
        
        if results:
            return json.loads(results[0]['result'])
        return None
    
    def cache_query(self, contract_address: str, query: str, result: Any):
        """Cache query result"""
        query_hash = hashlib.md5(f"{contract_address}_{query}".encode()).hexdigest()
        
        self.execute("""
            INSERT OR REPLACE INTO query_cache 
            (contract_address, query_hash, query, result, expires_at)
            VALUES (?, ?, ?, ?, datetime('now', '+24 hours'))
        """, (
            contract_address,
            query_hash,
            query,
            json.dumps(result)
        ))
    
    def get_sync_status(self, contract_address: str) -> Dict:
        """Get synchronization status"""
        results = self.execute("""
            SELECT last_synced_block, total_events, updated_at
            FROM contracts 
            WHERE contract_address = ?
        """, (contract_address,))
        
        if results:
            return dict(results[0])
        return {'last_synced_block': 0, 'total_events': 0, 'updated_at': None}
    
    def get_db_info(self) -> Dict:
        """Get database information"""
        tables = self.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            ORDER BY name
        """)
        
        total_tables = len(tables)
        
        events_count = self.execute("""
            SELECT SUM(total_events) as total 
            FROM contracts
        """)
        
        total_events = events_count[0]['total'] if events_count and events_count[0]['total'] else 0
        
        return {
            'db_file': self.db_file,
            'total_tables': total_tables,
            'total_events': total_events,
            'tables': [t['name'] for t in tables]
        }

# ============================================
# CONTRACT INDEXER
# ============================================

class ContractIndexer:
    """Indexes a smart contract and stores data in SQLite database"""
    
    def __init__(self, contract_address: str, abi: List[Dict], rpc_url: str, db: DatabaseManager):
        self.contract_address = contract_address
        self.abi = abi
        self.rpc_url = rpc_url
        self.db = db
        
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        if 'polygon' in rpc_url.lower() or 'matic' in rpc_url.lower():
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        if not self.w3.is_connected():
            raise Exception("Failed to connect to blockchain")
        
        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(contract_address),
            abi=abi
        )
        
        self.events = [item for item in abi if item.get('type') == 'event']
        self.view_functions = [
            item for item in abi 
            if item.get('type') == 'function' 
            and item.get('stateMutability') in ['view', 'pure']
        ]
        
        print(f"{Fore.GREEN}✅ Contract loaded: {contract_address}{Style.RESET_ALL}")
        print(f"   📝 Events: {len(self.events)}")
        print(f"   🔍 View Functions: {len(self.view_functions)}")
    
    def sync_historical(self, from_block: int = 0):
        """Sync all historical events"""
        print(f"\n{Fore.CYAN}📜 Syncing historical events from block {from_block}...{Style.RESET_ALL}")
        
        current_block = self.w3.eth.block_number
        batch_size = 10000
        total_events = 0
        
        for start in range(from_block, current_block, batch_size):
            end = min(start + batch_size, current_block)
            events_processed = self._sync_events(start, end)
            total_events += events_processed
            
            self.db.execute("""
                UPDATE contracts 
                SET last_synced_block = ?, total_events = total_events + ?
                WHERE contract_address = ?
            """, (end, events_processed, self.contract_address))
            
            print(f"   {Fore.YELLOW}Synced blocks {start}-{end} ({events_processed} events){Style.RESET_ALL}")
        
        print(f"{Fore.GREEN}✅ Historical sync complete! Total events: {total_events}{Style.RESET_ALL}")
        return total_events
    
    def _sync_events(self, from_block: int, to_block: int) -> int:
        """Sync events in a block range"""
        events_processed = 0
        
        for event in self.events:
            event_name = event['name']
            event_class = getattr(self.contract.events, event_name)
            
            try:
                events = event_class().get_logs(
                    fromBlock=from_block,
                    toBlock=to_block
                )
                
                for event_data in events:
                    self.db.store_event(self.contract_address, event_name, event_data)
                    events_processed += 1
                    
            except Exception as e:
                print(f"   {Fore.YELLOW}⚠️ Error fetching {event_name}: {e}{Style.RESET_ALL}")
        
        return events_processed
    
    def sync_realtime(self):
        """Continuously sync new events in real-time"""
        print(f"\n{Fore.CYAN}🔄 Starting real-time sync...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Press Ctrl+C to stop{Style.RESET_ALL}")
        
        last_block = self.db.get_sync_status(self.contract_address)['last_synced_block']
        if last_block == 0:
            last_block = self.w3.eth.block_number
        
        try:
            while True:
                current_block = self.w3.eth.block_number
                
                if current_block > last_block:
                    events_processed = self._sync_events(last_block + 1, current_block)
                    
                    if events_processed > 0:
                        print(f"{Fore.GREEN}   ✅ Synced {events_processed} events (Blocks {last_block+1}-{current_block}){Style.RESET_ALL}")
                    
                    self.db.execute("""
                        UPDATE contracts 
                        SET last_synced_block = ?, total_events = total_events + ?
                        WHERE contract_address = ?
                    """, (current_block, events_processed, self.contract_address))
                    
                    last_block = current_block
                
                time.sleep(2)
                
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⏹️ Stopped real-time sync{Style.RESET_ALL}")

# ============================================
# AI QUERY ENGINE
# ============================================

class AIQueryEngine:
    """Handles AI-powered queries"""
    
    def __init__(self, contract_address: str, abi: List[Dict], rpc_url: str, db: DatabaseManager, ollama_url: str, llm_model: str):
        self.contract_address = contract_address
        self.abi = abi
        self.rpc_url = rpc_url
        self.db = db
        self.ollama_url = ollama_url
        self.llm_model = llm_model
        
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        if 'polygon' in rpc_url.lower() or 'matic' in rpc_url.lower():
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(contract_address),
            abi=abi
        )
        
        self.view_functions = [
            item for item in abi 
            if item.get('type') == 'function' 
            and item.get('stateMutability') in ['view', 'pure']
        ]
        
        self.events = [item for item in abi if item.get('type') == 'event']
    
    def query(self, query: str) -> Dict:
        """Process a natural language query"""
        start_time = time.time()
        
        print(f"\n{Fore.CYAN}🔍 Processing: {query}{Style.RESET_ALL}")
        
        cached = self.db.get_cached_query(self.contract_address, query)
        if cached:
            print(f"{Fore.GREEN}📦 From cache{Style.RESET_ALL}")
            return cached
        
        analysis = self._analyze_query(query)
        
        if analysis['is_multi_function']:
            print(f"{Fore.BLUE}🔄 Multi-function query detected{Style.RESET_ALL}")
            result = self._handle_multi_function(query, analysis)
        else:
            print(f"{Fore.BLUE}🎯 Single function query{Style.RESET_ALL}")
            result = self._handle_single_function(query, analysis)
        
        if result and result.get('success'):
            self.db.cache_query(self.contract_address, query, result)
        
        result['time_taken'] = time.time() - start_time
        return result
    
    def _analyze_query(self, query: str) -> Dict:
        """Analyze query to determine requirements"""
        query_lower = query.lower()
        
        analysis = {
            'is_multi_function': False,
            'functions_needed': [],
            'params_needed': {},
            'needs_aggregation': False,
            'addresses': []
        }
        
        addresses = re.findall(r'0x[a-fA-F0-9]{40}', query)
        if addresses:
            analysis['addresses'] = addresses
        
        requirements = []
        
        if any(word in query_lower for word in ['user info', 'user details', 'profile', 'name', 'age']):
            requirements.append({
                'type': 'user_info',
                'function': 'getUserInfoByAddress',
                'params': ['address'],
                'description': 'User information (name, address, age)'
            })
        
        if any(word in query_lower for word in ['todos count', 'number of todos', 'how many todos', 'todo count', 'count todos']):
            requirements.append({
                'type': 'todos_count',
                'function': 'getTodosCountByAddress',
                'params': ['address'],
                'description': 'Number of todos'
            })
        
        if any(word in query_lower for word in ['todos', 'tasks', 'todo list']):
            requirements.append({
                'type': 'todos_list',
                'function': 'getUserTodosByAddress',
                'params': ['address'],
                'description': 'List of todos'
            })
        
        if 'balance' in query_lower:
            requirements.append({
                'type': 'balance',
                'function': 'balanceOf',
                'params': ['address'],
                'description': 'Balance'
            })
        
        if 'token' in query_lower:
            if 'name' in query_lower:
                requirements.append({
                    'type': 'token_name',
                    'function': 'name',
                    'params': [],
                    'description': 'Token name'
                })
            if 'symbol' in query_lower:
                requirements.append({
                    'type': 'token_symbol',
                    'function': 'symbol',
                    'params': [],
                    'description': 'Token symbol'
                })
        
        if any(word in query_lower for word in ['all users', 'every user', 'all addresses']):
            analysis['needs_all_users'] = True
            for func in self.view_functions:
                if func['name'] in ['getAllRegisteredUsers', 'getAllUsers', 'getUsers']:
                    analysis['all_users_function'] = func['name']
                    break
        
        if any(word in query_lower for word in ['top', 'most', 'average', 'avg', 'total']):
            analysis['needs_aggregation'] = True
            if 'top' in query_lower:
                limit_match = re.search(r'top\s+(\d+)', query_lower)
                analysis['top_limit'] = int(limit_match.group(1)) if limit_match else 5
        
        if len(requirements) > 1:
            analysis['is_multi_function'] = True
            analysis['functions_needed'] = requirements
        
        return analysis
    
    def _handle_single_function(self, query: str, analysis: Dict) -> Dict:
        """Handle single function query"""
        function_name, params = self._select_function_ai(query)
        
        if not function_name:
            function_name, params = self._keyword_match(query)
        
        if not function_name:
            return {
                'success': False,
                'query': query,
                'error': 'Could not determine which function to call',
                'available_functions': [f['name'] for f in self.view_functions]
            }
        
        try:
            result = self._call_function(function_name, params)
            formatted_result = self._format_result(result)
            
            return {
                'success': True,
                'source': 'rpc',
                'query': query,
                'function': function_name,
                'params': params,
                'result': formatted_result
            }
            
        except Exception as e:
            return {
                'success': False,
                'query': query,
                'error': str(e)
            }
    
    def _handle_multi_function(self, query: str, analysis: Dict) -> Dict:
        """Handle multi-function query"""
        result = {
            'success': True,
            'query': query,
            'source': 'multi_function',
            'data': {}
        }
        
        addresses = analysis.get('addresses', [])
        if not addresses and analysis.get('needs_all_users'):
            all_users_func = analysis.get('all_users_function')
            if all_users_func:
                try:
                    all_users = self._call_function(all_users_func, [])
                    if all_users and isinstance(all_users, (list, tuple)):
                        addresses = list(all_users)
                        print(f"{Fore.GREEN}   Found {len(addresses)} users{Style.RESET_ALL}")
                except:
                    pass
        
        if not addresses:
            address_match = re.search(r'0x[a-fA-F0-9]{40}', query)
            if address_match:
                addresses = [address_match.group()]
            else:
                for req in analysis['functions_needed']:
                    if not req['params']:
                        try:
                            func_result = self._call_function(req['function'], [])
                            result['data'][req['type']] = self._format_result(func_result)
                        except Exception as e:
                            result['data'][req['type']] = {'error': str(e)}
                
                if result['data']:
                    return result
                else:
                    return {'success': False, 'query': query, 'error': 'No address found in query'}
        
        for address in addresses:
            address_data = {'address': address}
            
            for req in analysis['functions_needed']:
                func_name = req['function']
                func_type = req['type']
                
                try:
                    params = []
                    if 'address' in req['params']:
                        params.append(address)
                    
                    func_result = self._call_function(func_name, params)
                    address_data[func_type] = self._format_result(func_result)
                    
                except Exception as e:
                    address_data[func_type] = {'error': str(e)}
            
            if analysis.get('needs_aggregation'):
                if 'todos_count' in address_data:
                    count = address_data['todos_count']
                    if isinstance(count, (int, float)):
                        result['_aggregation_data'] = result.get('_aggregation_data', [])
                        result['_aggregation_data'].append({
                            'address': address,
                            'count': count,
                            'data': address_data
                        })
            
            if len(addresses) > 1:
                result['data'][address] = address_data
            else:
                result['data'] = address_data
        
        if analysis.get('needs_aggregation') and result.get('_aggregation_data'):
            agg_data = result.pop('_aggregation_data')
            sorted_data = sorted(agg_data, key=lambda x: x['count'], reverse=True)
            
            top_limit = analysis.get('top_limit', 5)
            result['top_users'] = sorted_data[:top_limit]
            
            if 'average' in query.lower() or 'avg' in query.lower():
                total = sum(item['count'] for item in sorted_data)
                avg = total / len(sorted_data) if sorted_data else 0
                result['average'] = avg
            
            if 'total' in query.lower():
                result['total'] = sum(item['count'] for item in sorted_data)
            
            result['total_users'] = len(sorted_data)
        
        return result
    
    def _select_function_ai(self, query: str) -> Tuple[str, List[str]]:
        """Use AI to select function"""
        functions = self._get_function_descriptions()
        
        if not functions:
            return None, []
        
        prompt = f"""
You are a smart contract function selector.

CONTRACT FUNCTIONS:
{functions}

USER QUERY:
"{query}"

INSTRUCTIONS:
1. Select the best matching function
2. Extract required parameters from the query
3. Return ONLY JSON

Example response:
{{"function": "getUserTodosByAddress", "params": ["0x742d35Cc6634C0532925a3b844Bc9e7595f0b3f2"]}}

YOUR RESPONSE (JSON ONLY):
"""
        
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.llm_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0,
                        "num_predict": 150
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                text = response.json().get('response', '{}')
                json_match = re.search(r'\{[^{}]*\}', text)
                if json_match:
                    data = json.loads(json_match.group())
                    function_name = data.get('function')
                    params = data.get('params', [])
                    
                    if function_name and any(f['name'] == function_name for f in self.view_functions):
                        return function_name, params
            
            return None, []
            
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️ AI error: {e}{Style.RESET_ALL}")
            return None, []
    
    def _keyword_match(self, query: str) -> Tuple[str, List[str]]:
        """Fallback: Match function by keywords"""
        query_lower = query.lower()
        
        keyword_map = {
            'todos': ['getUserTodosByAddress', 'getUserTodos', 'getTodosByAddress'],
            'balance': ['balanceOf', 'getBalance', 'getUserBalance'],
            'name': ['name', 'getName', 'tokenName'],
            'symbol': ['symbol', 'getSymbol'],
            'total': ['totalSupply', 'getTotalSupply'],
            'owner': ['ownerOf', 'getOwner'],
            'count': ['getCount', 'getTotalCount', 'getUserCount'],
            'user info': ['getUserInfoByAddress', 'getUserInfo']
        }
        
        for keyword, function_names in keyword_map.items():
            if keyword in query_lower:
                for func_name in function_names:
                    if any(f['name'] == func_name for f in self.view_functions):
                        params = self._extract_params(query, func_name)
                        return func_name, params
        
        return None, []
    
    def _extract_params(self, query: str, function_name: str) -> List[str]:
        """Extract parameters from query"""
        func = next((f for f in self.view_functions if f['name'] == function_name), None)
        if not func:
            return []
        
        params = []
        for inp in func.get('inputs', []):
            param_type = inp.get('type', '')
            
            if param_type == 'address':
                address_match = re.search(r'0x[a-fA-F0-9]{40}', query)
                if address_match:
                    params.append(address_match.group())
                else:
                    params.append('')
            elif param_type in ['uint256', 'int256', 'uint', 'int']:
                number_match = re.search(r'\b\d+\b', query)
                if number_match:
                    params.append(number_match.group())
                else:
                    params.append('')
            else:
                params.append('')
        
        return [p for p in params if p]
    
    def _call_function(self, function_name: str, params: List[str]) -> Any:
        """Call contract function"""
        func = getattr(self.contract.functions, function_name)
        
        func_abi = next((f for f in self.view_functions if f['name'] == function_name), None)
        if not func_abi:
            func_abi = next((f for f in self.abi if f.get('name') == function_name), None)
        
        if not func_abi:
            raise Exception(f"Function {function_name} not found")
        
        converted_params = []
        expected_inputs = func_abi.get('inputs', [])
        
        for i, param in enumerate(params):
            if i < len(expected_inputs):
                param_type = expected_inputs[i].get('type', '')
                try:
                    if param_type == 'address':
                        converted_params.append(Web3.to_checksum_address(param))
                    elif param_type in ['uint256', 'int256', 'uint', 'int']:
                        converted_params.append(int(param) if param else 0)
                    elif param_type == 'bool':
                        converted_params.append(param.lower() == 'True')
                    else:
                        converted_params.append(param)
                except Exception as e:
                    print(f"{Fore.YELLOW}⚠️ Error converting param {i}: {e}{Style.RESET_ALL}")
                    converted_params.append(param)
        
        try:
            if converted_params:
                return func(*converted_params).call()
            else:
                return func().call()
        except Exception as e:
            raise Exception(f"Contract call failed: {str(e)}")
    
    def _format_result(self, result: Any) -> Any:
        """Format result for JSON serialization"""
        if isinstance(result, (bytes, bytearray)):
            try:
                return result.decode('utf-8')
            except:
                return '0x' + result.hex()
        elif isinstance(result, (list, tuple)):
            return [self._format_result(item) for item in result]
        elif hasattr(result, '_asdict'):
            return result._asdict()
        elif isinstance(result, dict):
            return {k: self._format_result(v) for k, v in result.items()}
        else:
            return result
    
    def _get_function_descriptions(self) -> str:
        """Get formatted function descriptions"""
        descriptions = []
        for func in self.view_functions:
            name = func['name']
            inputs = func.get('inputs', [])
            
            if inputs:
                params = [f"{inp.get('name', 'param')}:{inp.get('type', 'unknown')}" for inp in inputs]
                params_str = f"({', '.join(params)})"
            else:
                params_str = "()"
            
            descriptions.append(f"  • {name}{params_str}")
        
        return '\n'.join(descriptions)

# ============================================
# CHATBOT INTERFACE
# ============================================

class Chatbot:
    """Interactive chatbot interface"""
    
    def __init__(self, contract_address: str, query_engine: AIQueryEngine, db: DatabaseManager):
        self.contract_address = contract_address
        self.query_engine = query_engine
        self.db = db
        self.history = []
        
        print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🤖 AI CHATBOT INTERFACE{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Contract: {contract_address}{Style.RESET_ALL}")
        
        db_info = self.db.get_db_info()
        print(f"{Fore.GREEN}📁 Database: {db_info['db_file']}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}📊 Tables: {db_info['total_tables']} | Events: {db_info['total_events']}{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}💡 Example queries:{Style.RESET_ALL}")
        print(f"   • Get user info with number of todos for 0x...")
        print(f"   • Show me all todos for 0x...")
        print(f"   • Who are the top 5 users with most todos?")
        print(f"   • What is the average number of todos per user?")
        print(f"   • Show me all users with their todo counts")
        print(f"\n{Fore.YELLOW}Commands:{Style.RESET_ALL}")
        print(f"   • /help - Show this help")
        print(f"   • /history - Show query history")
        print(f"   • /clear - Clear history")
        print(f"   • /dbinfo - Show database info")
        print(f"   • /exit - Exit chatbot")
        print(f"\n{Fore.GREEN}Ready for queries!{Style.RESET_ALL}\n")
    
    def start(self):
        """Start the chatbot loop"""
        while True:
            try:
                query = input(f"{Fore.CYAN}You: {Style.RESET_ALL}").strip()
                
                if not query:
                    continue
                
                if query.lower() in ['/exit', '/quit', 'exit', 'quit']:
                    print(f"{Fore.YELLOW}👋 Goodbye!{Style.RESET_ALL}")
                    break
                
                if query.lower() == '/help':
                    self._show_help()
                    continue
                
                if query.lower() == '/history':
                    self._show_history()
                    continue
                
                if query.lower() == '/clear':
                    self.history = []
                    print(f"{Fore.GREEN}✅ History cleared{Style.RESET_ALL}")
                    continue
                
                if query.lower() == '/dbinfo':
                    self._show_db_info()
                    continue
                
                result = self.query_engine.query(query)
                
                self.history.append({
                    'query': query,
                    'response': result,
                    'timestamp': datetime.now().isoformat()
                })
                
                self._display_result(result)
                
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}👋 Goodbye!{Style.RESET_ALL}")
                break
            except Exception as e:
                print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
    
    def _display_result(self, result: Dict):
        """Display query result in a nice format"""
        print(f"\n{Fore.GREEN}{'─'*70}{Style.RESET_ALL}")
        
        if not result.get('success'):
            print(f"{Fore.RED}❌ {result.get('error', 'Unknown error')}{Style.RESET_ALL}")
            if 'available_functions' in result:
                print(f"{Fore.YELLOW}Available functions: {', '.join(result['available_functions'][:10])}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{'─'*70}{Style.RESET_ALL}\n")
            return
        
        source = result.get('source', 'unknown')
        if source == 'cache':
            print(f"{Fore.CYAN}📦 From cache{Style.RESET_ALL}")
        elif source == 'multi_function':
            print(f"{Fore.CYAN}🔄 Multi-function query{Style.RESET_ALL}")
        else:
            print(f"{Fore.CYAN}⚡ RPC call: {result.get('function', 'unknown')}{Style.RESET_ALL}")
        
        data = result.get('data', result.get('result', {}))
        
        if isinstance(data, dict):
            if 'address' in data:
                print(f"\n{Fore.YELLOW}Address: {data['address']}{Style.RESET_ALL}")
                del data['address']
            
            for key, value in data.items():
                if key.startswith('_'):
                    continue
                    
                if isinstance(value, dict):
                    print(f"\n{Fore.CYAN}📋 {key.replace('_', ' ').title()}:{Style.RESET_ALL}")
                    for k, v in value.items():
                        print(f"   {Fore.WHITE}{k}: {Fore.GREEN}{v}{Style.RESET_ALL}")
                elif isinstance(value, list):
                    print(f"\n{Fore.CYAN}📋 {key.replace('_', ' ').title()}:{Style.RESET_ALL}")
                    for item in value:
                        print(f"   • {Fore.GREEN}{item}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.CYAN}{key.replace('_', ' ').title()}: {Fore.GREEN}{value}{Style.RESET_ALL}")
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    print(f"\n{Fore.YELLOW}{'─'*40}{Style.RESET_ALL}")
                    for k, v in item.items():
                        print(f"{Fore.CYAN}{k}: {Fore.GREEN}{v}{Style.RESET_ALL}")
                else:
                    print(f"• {Fore.GREEN}{item}{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}{data}{Style.RESET_ALL}")
        
        if 'time_taken' in result:
            print(f"\n{Fore.YELLOW}⏱️ Time: {result['time_taken']:.2f}s{Style.RESET_ALL}")
        
        print(f"{Fore.GREEN}{'─'*70}{Style.RESET_ALL}\n")
    
    def _show_help(self):
        """Show help message"""
        print(f"\n{Fore.CYAN}📚 HELP{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'─'*70}{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Example Queries:{Style.RESET_ALL}")
        print(f"   • {Fore.WHITE}Get user info with number of todos for 0x742d35Cc6634C0532925a3b844Bc9e7595f0b3f2{Style.RESET_ALL}")
        print(f"   • {Fore.WHITE}Show me all todos for 0x742d35Cc6634C0532925a3b844Bc9e7595f0b3f2{Style.RESET_ALL}")
        print(f"   • {Fore.WHITE}Who are the top 5 users with most todos?{Style.RESET_ALL}")
        print(f"   • {Fore.WHITE}What is the average number of todos per user?{Style.RESET_ALL}")
        print(f"   • {Fore.WHITE}Show me all users with their todo counts{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Commands:{Style.RESET_ALL}")
        print(f"   • /help - Show this help")
        print(f"   • /history - Show query history")
        print(f"   • /clear - Clear history")
        print(f"   • /dbinfo - Show database info")
        print(f"   • /exit - Exit chatbot")
        print(f"{Fore.GREEN}{'─'*70}{Style.RESET_ALL}\n")
    
    def _show_history(self):
        """Show query history"""
        if not self.history:
            print(f"{Fore.YELLOW}No queries yet{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}📜 QUERY HISTORY{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'─'*70}{Style.RESET_ALL}")
        
        for i, entry in enumerate(self.history[-20:], 1):
            success = entry['response'].get('success', False)
            status = f"{Fore.GREEN}✅" if success else f"{Fore.RED}❌"
            print(f"{status} {Fore.WHITE}{i}. {entry['query'][:60]}{Style.RESET_ALL}")
        
        print(f"{Fore.GREEN}{'─'*70}{Style.RESET_ALL}\n")
    
    def _show_db_info(self):
        """Show database information"""
        db_info = self.db.get_db_info()
        
        print(f"\n{Fore.CYAN}📁 DATABASE INFO{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'─'*70}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}File: {Fore.GREEN}{db_info['db_file']}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Total Tables: {Fore.GREEN}{db_info['total_tables']}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Total Events: {Fore.GREEN}{db_info['total_events']}{Style.RESET_ALL}")
        
        if db_info['tables']:
            print(f"\n{Fore.WHITE}Tables:{Style.RESET_ALL}")
            for table in db_info['tables']:
                try:
                    count = self.db.execute(f"SELECT COUNT(*) as count FROM {table}")
                    row_count = count[0]['count'] if count else 0
                    print(f"   • {Fore.GREEN}{table}{Style.RESET_ALL} ({row_count} rows)")
                except:
                    print(f"   • {Fore.GREEN}{table}{Style.RESET_ALL}")
        
        print(f"{Fore.GREEN}{'─'*70}{Style.RESET_ALL}\n")

# ============================================
# MAIN APPLICATION
# ============================================

def main():
    """Main application - Hardcoded config + Chatbot CLI"""
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🚀 UNIVERSAL AI SMART CONTRACT INDEXER & CHATBOT{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Version: 1.0.0 (Hardcoded Config){Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    
    print(f"\n{Fore.GREEN}📋 Configuration:{Style.RESET_ALL}")
    print(f"   Contract: {Fore.WHITE}{CONTRACT_ADDRESS}{Style.RESET_ALL}")
    print(f"   RPC: {Fore.WHITE}{RPC_URL}{Style.RESET_ALL}")
    print(f"   Database: {Fore.WHITE}{DB_FILE}{Style.RESET_ALL}")
    print(f"   AI Model: {Fore.WHITE}{LLM_MODEL}{Style.RESET_ALL}")
    
    # Initialize database
    db = DatabaseManager(DB_FILE)
    
    # Create tables
    db.create_tables(CONTRACT_ADDRESS, CONTRACT_ABI)
    
    # Initialize indexer
    print(f"\n{Fore.CYAN}🔄 Initializing indexer...{Style.RESET_ALL}")
    try:
        indexer = ContractIndexer(CONTRACT_ADDRESS, CONTRACT_ABI, RPC_URL, db)
    except Exception as e:
        print(f"{Fore.RED}❌ Failed to initialize indexer: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Make sure:{Style.RESET_ALL}")
        print(f"   1. Contract address is correct")
        print(f"   2. RPC URL is accessible")
        print(f"   3. You're connected to the internet")
        sys.exit(1)
    
    # Sync options
    print(f"\n{Fore.CYAN}📥 Sync Options{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}1. Sync all historical events (recommended){Style.RESET_ALL}")
    print(f"{Fore.YELLOW}2. Start from latest block only (faster){Style.RESET_ALL}")
    print(f"{Fore.YELLOW}3. Skip sync (use existing data){Style.RESET_ALL}")
    
    sync_choice = input(f"{Fore.WHITE}Choose option [1]: {Style.RESET_ALL}").strip() or '1'
    
    if sync_choice == '1':
        from_block = input(f"{Fore.WHITE}Start from block [0]: {Style.RESET_ALL}").strip() or '0'
        try:
            indexer.sync_historical(int(from_block))
        except Exception as e:
            print(f"{Fore.RED}❌ Sync failed: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Continuing with partial data...{Style.RESET_ALL}")
    elif sync_choice == '2':
        print(f"{Fore.YELLOW}Starting from latest block{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}Skipping initial sync{Style.RESET_ALL}")
    
    # Start real-time sync in background
    print(f"\n{Fore.CYAN}🔄 Starting real-time sync...{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}⚠️ Real-time sync will run in background{Style.RESET_ALL}")
    
    import threading
    sync_thread = threading.Thread(target=indexer.sync_realtime, daemon=True)
    sync_thread.start()
    
    time.sleep(1)
    
    # Test Ollama connection
    print(f"\n{Fore.CYAN}🤖 Testing AI connection...{Style.RESET_ALL}")
    try:
        response = requests.get(OLLAMA_URL.replace('/api/generate', '/api/tags'), timeout=5)
        if response.status_code == 200:
            print(f"{Fore.GREEN}✅ Ollama is running{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠️ Ollama may not be running properly{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}   The AI will fall back to keyword matching{Style.RESET_ALL}")
    except:
        print(f"{Fore.YELLOW}⚠️ Could not connect to Ollama{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}   Start with: ollama serve{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}   The AI will fall back to keyword matching{Style.RESET_ALL}")
    
    # Initialize query engine
    query_engine = AIQueryEngine(CONTRACT_ADDRESS, CONTRACT_ABI, RPC_URL, db, OLLAMA_URL, LLM_MODEL)
    
    # Start chatbot
    chatbot = Chatbot(CONTRACT_ADDRESS, query_engine, db)
    chatbot.start()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Goodbye!{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Fatal error: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        sys.exit(1)